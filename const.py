"""Constants for the FSolar integration."""
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

DOMAIN = "fsolar"

# Configuration
CONF_EMAIL = "email"
CONF_PASSWORD = "password"

# Battery attributes
ATTR_BATTERY_SOC = "battery_soc"
ATTR_BATTERY_VOLTAGE = "battery_voltage"
ATTR_BATTERY_CURRENT = "battery_current"
ATTR_BATTERY_POWER = "battery_power"
ATTR_BATTERY_TEMPERATURE = "battery_temperature"
ATTR_BATTERY_CAPACITY = "battery_capacity"
ATTR_BATTERY_STATUS = "battery_status"
ATTR_BATTERY_MODE = "battery_mode"
ATTR_CHARGING_POWER = "charging_power"
ATTR_DISCHARGING_POWER = "discharging_power"
ATTR_TOTAL_CHARGE = "total_charge"
ATTR_TOTAL_DISCHARGE = "total_discharge"
ATTR_CYCLES = "cycles"
ATTR_HEALTH = "health"
ATTR_TIME_REMAINING = "time_remaining"

# Sensor types
SENSOR_TYPES = {
    "battery_soc": {
        "name": "Battery State of Charge",
        "unit": PERCENTAGE,
        "icon": "mdi:battery",
        "device_class": "battery",
        "state_class": "measurement",
    },
    "battery_voltage": {
        "name": "Battery Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:lightning-bolt",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "battery_current": {
        "name": "Battery Current",
        "unit": UnitOfElectricCurrent.AMPERE,
        "icon": "mdi:current-dc",
        "device_class": "current",
        "state_class": "measurement",
    },
    "battery_power": {
        "name": "Battery Power",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:flash",
        "device_class": "power",
        "state_class": "measurement",
    },
    "battery_temperature": {
        "name": "Battery Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "battery_capacity": {
        "name": "Battery Capacity",
        "unit": "Ah",
        "icon": "mdi:battery-high",
        "device_class": None,
        "state_class": "total",
    },
    "battery_capacity_kwh": {
        "name": "Battery Capacity kWh",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-high",
        "device_class": "energy_storage",
        "state_class": "total",
    },
    "battery_remaining_kwh": {
        "name": "Battery Remaining kWh",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery",
        "device_class": "energy",
        "state_class": "measurement",
    },
    "daily_charge_kwh": {
        "name": "Daily Charge",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-charging",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "daily_discharge_kwh": {
        "name": "Daily Discharge",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-minus",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "cycles": {
        "name": "Battery Cycles",
        "unit": "cycles",
        "icon": "mdi:counter",
        "state_class": "total_increasing",
    },
    "health": {
        "name": "Battery Health",
        "unit": PERCENTAGE,
        "icon": "mdi:battery-heart-variant",
        "state_class": "measurement",
    },
    "charging_status": {
        "name": "Charging Status",
        "unit": None,
        "icon": "mdi:battery-charging",
        "device_class": None,
        "state_class": None,
    },
    "time_remaining": {
        "name": "Time Remaining",
        "unit": UnitOfTime.HOURS,
        "icon": "mdi:timer-outline",
        "device_class": "duration",
        "state_class": "measurement",
    },
}

# Battery status mapping (bmsChargingState)
BATTERY_CHARGING_STATUS = {
    0: "Standby",
    1: "Charging",
    2: "Discharging",
}

# Device status mapping
DEVICE_STATUS = {
    "NM": "Normal",
    "AL": "Alarm",
    "FL": "Fault",
    "OF": "Offline",
}

# Battery modes
BATTERY_MODES = [
    "self_use",
    "backup",
    "charge",
    "discharge",
    "auto",
]
