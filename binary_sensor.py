"""Binary sensor platform for FSolar integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .sensor import extract_battery_data

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class FSolarBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing FSolar binary sensor entities."""
    value_fn: Callable[[dict], bool | None] = lambda data: None


BINARY_SENSOR_DESCRIPTIONS: tuple[FSolarBinarySensorEntityDescription, ...] = (
    FSolarBinarySensorEntityDescription(
        key="battery_charging",
        name="Battery Charging",
        translation_key="battery_charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda data: (
            int(s) == 1
            if (s := data.get("bmsChargingState")) is not None
            else None
        ),
    ),
    FSolarBinarySensorEntityDescription(
        key="battery_discharging",
        name="Battery Discharging",
        translation_key="battery_discharging",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: (
            int(s) == 2
            if (s := data.get("bmsChargingState")) is not None
            else None
        ),
    ),
    FSolarBinarySensorEntityDescription(
        key="battery_low",
        name="Battery Low",
        translation_key="battery_low",
        device_class=BinarySensorDeviceClass.BATTERY,
        # Threshold is evaluated at runtime in FSolarBinarySensor
        value_fn=lambda data: None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FSolar binary sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device_id, device_data in coordinator.data.items():
        device_info = device_data["device_info"]
        for desc in BINARY_SENSOR_DESCRIPTIONS:
            entities.append(
                FSolarBinarySensor(coordinator, device_id, device_info, desc, entry)
            )

    async_add_entities(entities)


class FSolarBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for FSolar integration."""

    entity_description: FSolarBinarySensorEntityDescription

    def __init__(
        self,
        coordinator,
        device_id: str,
        device_info: dict[str, Any],
        description: FSolarBinarySensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._device_info = device_info
        self._attr_unique_id = f"{device_id}_{description.key}"
        self._attr_has_entity_name = True

        # Options for battery_low threshold
        self._use_safety_reserve = entry.options.get("use_safety_reserve", False)
        self._safety_reserve_percent = float(entry.options.get("safety_reserve_percent", 10))

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_info.get("alias") or self._device_info.get("deviceSn", f"Battery {self._device_id}"),
            manufacturer="Felicity Solar",
            model=self._device_info.get("deviceModel", "FSolar Battery"),
            sw_version=self._device_info.get("moduleVersion") or self._device_info.get("ctVersion", "Unknown"),
        )

    @property
    def available(self) -> bool:
        """Return availability."""
        return self.coordinator.last_update_success and self._device_id in self.coordinator.data

    @property
    def is_on(self) -> bool | None:
        """Return the state of the binary sensor."""
        data = extract_battery_data(self.coordinator.data, self._device_id)
        if not data:
            return None

        # Special handling for battery_low — uses configurable threshold
        if self.entity_description.key == "battery_low":
            soc_raw = data.get("battSoc") or data.get("emsSoc")
            if soc_raw is None:
                return None
            soc = float(soc_raw)
            threshold = (
                self._safety_reserve_percent
                if self._use_safety_reserve
                else 20.0
            )
            return soc <= threshold

        return self.entity_description.value_fn(data)
