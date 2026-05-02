"""DataUpdateCoordinator for FSolar integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .api import FSolarAPI

_LOGGER = logging.getLogger(__name__)

class FSolarDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching FSolar data."""

    def __init__(self, hass: HomeAssistant, api: FSolarAPI) -> None:
        """Initialize."""
        # Get scan interval from options or use default
        scan_interval_minutes = 5

        # Try to read from the config_entry associated with this API instance
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.data.get("username") == api.username:
                scan_interval_minutes = entry.options.get("scan_interval", 5)
                break

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval_minutes),
        )
        self.api = api
        self.last_successful_update: datetime | None = None

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            # Ensure we are authenticated before fetching
            if not self.api.is_authenticated:
                _LOGGER.debug("Not authenticated, logging in...")
                await self.api.login()

            # Fetch device list
            _LOGGER.debug("Fetching device list...")
            devices = await self.api.get_devices()
            _LOGGER.info("Found %d devices", len(devices))

            # Fetch data for each battery / inverter
            battery_data = {}
            for device in devices:
                device_sn = device.get("deviceSn")
                device_type = device.get("deviceType", "BP")  # BP = Battery Pack

                if device_sn:
                    _LOGGER.debug("Fetching data for device: %s (type: %s)", device_sn, device_type)
                    data = await self.api.get_battery_data(device_sn, device_type)

                    # Extract nameplate values directly from the API response.
                    # Known fields: volt="25.6", rateVolt="24", ratedEnergy="2.56"
                    raw_data = data.get("data", data) if isinstance(data, dict) else data

                    nominal_voltage = None
                    for field in ("volt", "rateVolt"):
                        val = raw_data.get(field) if isinstance(raw_data, dict) else None
                        if val is not None:
                            try:
                                nominal_voltage = float(val)
                                _LOGGER.debug(
                                    "Nominal voltage for %s detected from API ('%s'): %sV",
                                    device_sn, field, nominal_voltage,
                                )
                                break
                            except (ValueError, TypeError):
                                pass

                    rated_energy_kwh = None
                    if isinstance(raw_data, dict) and (re_val := raw_data.get("ratedEnergy")):
                        try:
                            rated_energy_kwh = float(re_val)
                            _LOGGER.debug(
                                "Rated energy for %s from API: %s kWh", device_sn, rated_energy_kwh
                            )
                        except (ValueError, TypeError):
                            pass

                    battery_data[device_sn] = {
                        "device_info": device,
                        "battery_data": data,
                        "nominal_voltage": nominal_voltage,
                        "rated_energy_kwh": rated_energy_kwh,
                    }
                else:
                    _LOGGER.warning("Device without deviceSn: %s", device)

            # Record the timestamp of the last successful update
            self.last_successful_update = dt_util.utcnow()
            _LOGGER.info("Successfully updated data for %d devices", len(battery_data))
            return battery_data

        except Exception as err:
            _LOGGER.error("Error communicating with API: %s", err, exc_info=True)
            raise UpdateFailed(f"Error communicating with API: {err}")
