from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, SCAN_INTERVAL
import datetime

class FSolarCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api, device_sn, logger):
        super().__init__(
            hass,
            logger=logger,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.api = api
        self.device_sn = device_sn

    async def _async_update_data(self):
        def fetch():
            payload_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.api.get_device_snapshot(
                device_sn=self.device_sn,
                device_type="BP",
                date_str=payload_time
            )
            return self.api.snapshot_data

        try:
            return await self.hass.async_add_executor_job(fetch)
        except Exception as err:
            raise UpdateFailed(f"FSolar update failed: {err}")
