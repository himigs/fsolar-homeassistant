"""FSolar Battery Integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .api import FSolarAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]
SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FSolar from a config entry."""
    # Obter sessão aiohttp
    session = async_get_clientsession(hass)
    
    # Criar API client
    api = FSolarAPI(
        username=entry.data["username"],
        password=entry.data["password"],
        session=session,
        password_encrypted=entry.data.get("password_encrypted", False),
    )

    # Criar coordinator
    coordinator = FSolarDataUpdateCoordinator(hass, api)
    
    # Primeira atualização
    await coordinator.async_config_entry_first_refresh()

    # Armazenar coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class FSolarDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching FSolar data."""

    def __init__(self, hass: HomeAssistant, api: FSolarAPI) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            # Garantir que está autenticado
            if not self.api.is_authenticated:
                _LOGGER.debug("Not authenticated, logging in...")
                await self.api.login()
            
            # Buscar lista de dispositivos
            _LOGGER.debug("Fetching device list...")
            devices = await self.api.get_devices()
            _LOGGER.info("Found %d devices", len(devices))
            
            # Buscar dados de cada bateria/inversor
            battery_data = {}
            for device in devices:
                # O deviceSn vem diretamente no objeto
                device_sn = device.get("deviceSn")
                device_type = device.get("deviceType", "BP")  # BP = Battery Pack
                
                if device_sn:
                    _LOGGER.debug("Fetching data for device: %s (type: %s)", device_sn, device_type)
                    data = await self.api.get_battery_data(device_sn, device_type)
                    battery_data[device_sn] = {
                        "device_info": device,
                        "battery_data": data,
                    }
                else:
                    _LOGGER.warning("Device without deviceSn: %s", device)
            
            _LOGGER.info("Successfully updated data for %d devices", len(battery_data))
            return battery_data
            
        except Exception as err:
            _LOGGER.error("Error communicating with API: %s", err, exc_info=True)
            raise UpdateFailed(f"Error communicating with API: {err}")