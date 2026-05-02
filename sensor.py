"""Sensor platform for FSolar integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

from .const import DOMAIN, BATTERY_CHARGING_STATUS

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class FSolarSensorEntityDescription(SensorEntityDescription):
    """Class describing FSolar sensor entities."""
    value_fn: Callable[[dict, float], Any] | None = None
    precision: int | None = None


def extract_battery_data(coordinator_data: dict, device_id: str) -> dict:
    if device_id not in coordinator_data:
        return {}
    battery_data = coordinator_data[device_id].get("battery_data", {})
    return battery_data.get("data", battery_data) if isinstance(battery_data, dict) else battery_data


SENSOR_DESCRIPTIONS: tuple[FSolarSensorEntityDescription, ...] = (
    # ========================================================
    # MAIN PANEL (Core Dynamic Sensors)
    # ========================================================
    FSolarSensorEntityDescription(
        key="battery_soc",
        name="Battery State of Charge",
        translation_key="battery_soc",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data, _: data.get("battSoc") or data.get("emsSoc"),
    ),
    FSolarSensorEntityDescription(
        key="battery_remaining_kwh",
        name="Battery Remaining kWh",
        translation_key="battery_remaining_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:battery",
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
        value_fn=lambda data, nom_v: ((float(cap) * nom_v) / 1000 * float(soc) / 100) if (cap := data.get("battCapacity") or data.get("emsCapacity") or data.get("totalEmsCapacity")) and (soc := data.get("battSoc") or data.get("emsSoc")) else None,
    ),
    FSolarSensorEntityDescription(
        key="time_to_full",
        name="Time to Full",
        translation_key="time_to_full",
        native_unit_of_measurement=UnitOfTime.HOURS,
        icon="mdi:battery-charging",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    FSolarSensorEntityDescription(
        key="time_to_empty",
        name="Time to Empty",
        translation_key="time_to_empty",
        native_unit_of_measurement=UnitOfTime.HOURS,
        icon="mdi:battery-arrow-down",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    FSolarSensorEntityDescription(
        key="charging_status",
        name="Charging Status",
        translation_key="charging_status",
        icon="mdi:battery-charging",
        value_fn=lambda data, _: BATTERY_CHARGING_STATUS.get(int(status), "Unknown") if (status := data.get("bmsChargingState")) is not None else None,
    ),
    FSolarSensorEntityDescription(
        key="battery_power",
        name="Battery Power",
        translation_key="battery_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:flash",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data, _: data.get("bmsPower") or data.get("emsPower"),
    ),
    FSolarSensorEntityDescription(
        key="battery_voltage",
        name="Battery Voltage",
        translation_key="battery_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:lightning-bolt",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
        value_fn=lambda data, _: data.get("battVolt") or data.get("emsVoltage"),
    ),
    FSolarSensorEntityDescription(
        key="battery_current",
        name="Battery Current",
        translation_key="battery_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:current-dc",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
        value_fn=lambda data, _: data.get("battCurr") or data.get("emsCurrent"),
    ),
    FSolarSensorEntityDescription(
        key="daily_charge_kwh",
        name="Daily Charge",
        translation_key="daily_charge_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:battery-charging",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=2,
    ),
    FSolarSensorEntityDescription(
        key="daily_discharge_kwh",
        name="Daily Discharge",
        translation_key="daily_discharge_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:battery-minus",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=2,
    ),
    FSolarSensorEntityDescription(
        key="battery_temperature",
        name="Battery Temperature",
        translation_key="battery_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
        value_fn=lambda data, _: data.get("tempMax") or data.get("tempMin"),
    ),

    # ========================================================
    # DIAGNOSTIC PANEL (Static Specs & Health Sensors)
    # ========================================================
    FSolarSensorEntityDescription(
        key="battery_capacity",
        name="Battery Capacity",
        translation_key="battery_capacity",
        native_unit_of_measurement="Ah",
        icon="mdi:battery-high",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data, _: data.get("battCapacity") or data.get("emsCapacity") or data.get("totalEmsCapacity"),
    ),
    FSolarSensorEntityDescription(
        key="battery_capacity_kwh",
        name="Battery Capacity kWh",
        translation_key="battery_capacity_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:battery-high",
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        precision=2,
        value_fn=lambda data, nom_v: (float(cap) * nom_v) / 1000 if (cap := data.get("battCapacity") or data.get("emsCapacity") or data.get("totalEmsCapacity")) else None,
    ),
    FSolarSensorEntityDescription(
        key="health",
        name="Battery Health",
        translation_key="health",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-heart-variant",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data, _: data.get("battSoh") or data.get("emsSoh"),
    ),
    FSolarSensorEntityDescription(
        key="cycles",
        name="Battery Cycles",
        translation_key="cycles",
        native_unit_of_measurement="cycles",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data, _: data.get("batCycleIndex") or data.get("batFullCount"),
    ),
    FSolarSensorEntityDescription(
        key="charge_voltage_limit",
        name="Charge Voltage Limit",
        translation_key="charge_voltage_limit",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:car-battery",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        precision=1,
        value_fn=lambda data, _: data.get("BMSLCVolt") or data.get("bMSLCVolt"),
    ),
    FSolarSensorEntityDescription(
        key="discharge_voltage_limit",
        name="Discharge Voltage Limit",
        translation_key="discharge_voltage_limit",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:car-battery",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        precision=1,
        value_fn=lambda data, _: data.get("BMSLDVolt") or data.get("bMSLDVolt"),
    ),
    FSolarSensorEntityDescription(
        key="charge_current_limit",
        name="Charge Current Limit",
        translation_key="charge_current_limit",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:current-dc",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        precision=1,
        value_fn=lambda data, _: data.get("BMSLCCurr") or data.get("bMSLCCurr"),
    ),
    FSolarSensorEntityDescription(
        key="discharge_current_limit",
        name="Discharge Current Limit",
        translation_key="discharge_current_limit",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:current-dc",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        precision=1,
        value_fn=lambda data, _: data.get("BMSLDCurr") or data.get("bMSLDCurr"),
    ),
    FSolarSensorEntityDescription(
        key="max_cell_voltage",
        name="Max Cell Voltage",
        translation_key="max_cell_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:battery-plus",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        precision=3,
        value_fn=lambda data, _: round(float(val) / 1000.0, 3) if (val := data.get("maxVoltage2bms")) else None,
    ),
    FSolarSensorEntityDescription(
        key="min_cell_voltage",
        name="Min Cell Voltage",
        translation_key="min_cell_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:battery-minus",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        precision=3,
        value_fn=lambda data, _: round(float(val) / 1000.0, 3) if (val := data.get("minVoltage2bms")) else None,
    ),
    FSolarSensorEntityDescription(
        key="max_cell_temp",
        name="Max Cell Temp",
        translation_key="max_cell_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        precision=1,
        value_fn=lambda data, _: data.get("tempMax"),
    ),
    FSolarSensorEntityDescription(
        key="min_cell_temp",
        name="Min Cell Temp",
        translation_key="min_cell_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        precision=1,
        value_fn=lambda data, _: data.get("tempMin"),
    ),
    FSolarSensorEntityDescription(
        key="heat_current",
        name="Heat Current",
        translation_key="heat_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:heating-coil",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        precision=1,
        value_fn=lambda data, _: data.get("heatCurr"),
    ),
)


CELL_DESCRIPTIONS = []
for i in range(1, 17):
    idx = i - 1
    CELL_DESCRIPTIONS.append(FSolarSensorEntityDescription(
        key=f"cell_{i}_voltage",
        name=f"Cell {i} Voltage",
        translation_key=f"cell_{i}_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:battery-outline",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        precision=3,
        value_fn=lambda data, _, i=idx: round(float(val[0]) / 1000.0, 3) if (val := (data.get("bmsVoltageList") or [])[i:i+1]) and val[0] and str(val[0]) != "32767" else None
    ))
for i in range(1, 5):
    idx = i - 1
    CELL_DESCRIPTIONS.append(FSolarSensorEntityDescription(
        key=f"cell_{i}_temp",
        name=f"Cell {i} Temperature",
        translation_key=f"cell_{i}_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        precision=1,
        value_fn=lambda data, _, i=idx: float(val[0]) if (val := (data.get("cellTempList") or [])[i:i+1]) and val[0] and str(val[0]) not in ("3276.7", "32767") else None
    ))

ALL_DESCRIPTIONS = SENSOR_DESCRIPTIONS + tuple(CELL_DESCRIPTIONS)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FSolar sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device_id, device_data in coordinator.data.items():
        device_info = device_data["device_info"]
        
        for desc in ALL_DESCRIPTIONS:
            if desc.key in ("daily_charge_kwh", "daily_discharge_kwh"):
                entities.append(FSolarDailyEnergySensor(coordinator, device_id, device_info, desc, entry))
            elif desc.key in ("time_to_full", "time_to_empty"):
                entities.append(FSolarTimeRemainingSensor(coordinator, device_id, device_info, desc, entry))
            else:
                entities.append(FSolarSensor(coordinator, device_id, device_info, desc, entry))

    async_add_entities(entities)


class FSolarBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for FSolar sensors."""

    entity_description: FSolarSensorEntityDescription

    def __init__(
        self,
        coordinator,
        device_id: str,
        device_info: dict[str, Any],
        description: FSolarSensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._device_info = device_info
        
        # Nominal voltage priority: auto-detected from API > saved in options (legacy) > default 25.6V
        api_voltage = (
            coordinator.data.get(device_id, {}).get("nominal_voltage")
            if coordinator.data
            else None
        )
        options_voltage = entry.options.get("nominal_voltage")
        if api_voltage is not None:
            self._nominal_voltage = float(api_voltage)
        elif options_voltage is not None:
            self._nominal_voltage = float(options_voltage)
        else:
            self._nominal_voltage = 25.6
        
        self._attr_unique_id = f"{device_id}_{description.key}"
        self._attr_has_entity_name = True

        if description.precision is not None:
            self._attr_suggested_display_precision = description.precision

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_info.get("alias") or self._device_info.get("deviceSn", f"Battery {self._device_id}"),
            manufacturer="Felicity Solar",
            model=self._device_info.get("deviceModel", "FSolar Battery"),
            sw_version=self._device_info.get("moduleVersion") or self._device_info.get("ctVersion", "Unknown"),
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self._device_id in self.coordinator.data


class FSolarSensor(FSolarBaseSensor):
    """Standard FSolar sensor mapping values from API directly."""

    @property
    def native_value(self):
        data = extract_battery_data(self.coordinator.data, self._device_id)
        if not data or not self.entity_description.value_fn:
            return None

        val = self.entity_description.value_fn(data, self._nominal_voltage)
        if val is not None:
            try:
                if isinstance(val, str) and val.replace('.','',1).lstrip('-').isdigit():
                    fval = float(val)
                    if fval < -999 or fval > 999999 or (self.entity_description.key == "battery_temperature" and fval > 100):
                        return None
                    return fval
                return float(val) if isinstance(val, (int, float)) else val
            except (ValueError, TypeError):
                pass
        return val


class FSolarTimeRemainingSensor(FSolarBaseSensor):
    """Calculates time remaining for charging or discharging."""

    def __init__(self, coordinator, device_id, device_info, description, entry) -> None:
        super().__init__(coordinator, device_id, device_info, description, entry)
        self._use_safety_reserve = entry.options.get("use_safety_reserve", False)
        self._safety_reserve_percent = float(entry.options.get("safety_reserve_percent", 10))

    @property
    def icon(self) -> str | None:
        return self.entity_description.icon

    @property
    def native_value(self):
        data = extract_battery_data(self.coordinator.data, self._device_id)
        if not data:
            return None
            
        try:
            soc = data.get("battSoc") or data.get("emsSoc")
            capacity = data.get("battCapacity") or data.get("emsCapacity") or data.get("totalEmsCapacity")
            state = data.get("bmsChargingState")
            voltage = data.get("battVolt") or data.get("emsVoltage")
            
            if soc is None or capacity is None or state is None:
                return None
                
            soc, cap, volt = float(soc), float(capacity), float(voltage or 25.6)
            cap_kwh = (cap * volt / 1000) if cap > 50 else cap
            
            if state == 0:
                return None
                
            is_to_empty = self.entity_description.key == "time_to_empty"
            is_to_full = self.entity_description.key == "time_to_full"

            if is_to_empty:
                if state != 2:
                    return None
                
                # Apply safety reserve (DOD limit)
                if self._use_safety_reserve:
                    if soc <= self._safety_reserve_percent:
                        return 0.0
                    available_soc_fraction = (soc - self._safety_reserve_percent) / 100
                else:
                    available_soc_fraction = soc / 100

                current = abs(float(data.get("batDisCurrent") or data.get("batDischargeCurrent") or data.get("battCurr") or 0))
                if current > 0:
                    return round((cap_kwh * 1000 / volt * available_soc_fraction) / current, 2)
                
                power = abs(float(data.get("batDisPower") or data.get("bmsPowerDischarge") or data.get("bmsPower") or 0))
                if power > 0:
                    return round((available_soc_fraction * cap_kwh * 1000) / power, 2)
                    
            elif is_to_full:
                if state != 1:
                    return None

                current = abs(float(data.get("batCharCurrent") or data.get("batChargeCurrent") or data.get("battCurr") or 0))
                if current > 0:
                    return round((cap_kwh * 1000 / volt * ((100 - soc) / 100)) / current, 2)
                    
                power = abs(float(data.get("batCharPower") or data.get("bmsPowerCharging") or data.get("bmsPower") or 0))
                if power > 0:
                    return round((((100 - soc) / 100) * cap_kwh * 1000) / power, 2)

        except (ValueError, TypeError, ZeroDivisionError):
            pass
            
        return None


class FSolarDailyEnergySensor(FSolarBaseSensor, RestoreEntity):
    """Accumulates energy over a day."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._daily_energy = 0.0
        self._last_power = 0.0
        self._last_update = None
        self._last_reset_date = dt_util.now().date().isoformat()
        self._is_charge = self.entity_description.key == "daily_charge_kwh"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            try:
                val = float(last_state.state)
                if 0 <= val <= 1000:
                    self._daily_energy = val
                
                if attrs := last_state.attributes:
                    self._last_reset_date = attrs.get("last_reset_date", self._last_reset_date)
                    self._last_power = float(attrs.get("last_power", 0))
                    if update_str := attrs.get("last_update"):
                        self._last_update = dt_util.parse_datetime(update_str)
            except (ValueError, TypeError):
                pass
                
        today = dt_util.now().date().isoformat()
        if self._last_reset_date != today:
            self._daily_energy = 0.0
            self._last_reset_date = today
            self._last_power = 0.0
            self._last_update = None

    @property
    def native_value(self):
        data = extract_battery_data(self.coordinator.data, self._device_id)
        if not data:
            return round(self._daily_energy, 3)

        now = dt_util.now()
        today = now.date().isoformat()
        
        if self._last_reset_date != today:
            self._daily_energy = 0.0
            self._last_reset_date = today
            self._last_power = 0.0
            self._last_update = now

        power = 0.0
        if self._is_charge:
            p_val = data.get("batCharPower") or data.get("bmsPowerCharging") or data.get("chargingPower")
            if not p_val and data.get("bmsChargingState") == 1 and data.get("bmsPower"):
                p_val = abs(float(data.get("bmsPower")))
            power = float(p_val or 0)
        else:
            p_val = data.get("batDisPower") or data.get("bmsPowerDischarge") or data.get("dischargingPower")
            if not p_val and data.get("bmsChargingState") == 2 and data.get("bmsPower"):
                p_val = abs(float(data.get("bmsPower")))
            power = float(p_val or 0)

        if self._last_update and power > 0:
            time_delta = (now - self._last_update).total_seconds() / 3600
            if time_delta <= 0.25:
                avg_power = (power + self._last_power) / 2
                self._daily_energy += (avg_power * time_delta) / 1000

        self._last_power = power
        self._last_update = now

        return round(self._daily_energy, 3)

    @property
    def extra_state_attributes(self):
        attrs = {}
        if self._last_reset_date:
            attrs["last_reset_date"] = self._last_reset_date
        if self._last_update:
            attrs["last_update"] = self._last_update.isoformat()
        if self._last_power:
            attrs["last_power"] = round(self._last_power, 1)
        return attrs
