"""Sensor platform for FSolar integration."""
from __future__ import annotations

import logging
from datetime import datetime, time as dt_time
from typing import Any

from homeassistant.components.sensor import SensorEntity, RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SENSOR_TYPES, BATTERY_CHARGING_STATUS, DEVICE_STATUS

_LOGGER = logging.getLogger(__name__)


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
        
        # Criar sensores para cada tipo
        for sensor_type, sensor_config in SENSOR_TYPES.items():
            entities.append(
                FSolarSensor(
                    coordinator,
                    device_id,
                    device_info,
                    sensor_type,
                    sensor_config,
                    entry,  # Passar o config entry
                )
            )

    async_add_entities(entities)


class FSolarSensor(CoordinatorEntity, RestoreEntity, SensorEntity):
    """Representation of a FSolar sensor."""

    def __init__(
        self,
        coordinator,
        device_id: str,
        device_info: dict[str, Any],
        sensor_type: str,
        sensor_config: dict[str, Any],
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_info = device_info
        self._sensor_type = sensor_type
        self._sensor_config = sensor_config
        self._entry = entry
        
        # Obter tensão nominal das options (configurável) ou usar padrão 25.6V
        nominal_voltage_str = entry.options.get("nominal_voltage", "25.6")
        self._nominal_voltage = float(nominal_voltage_str)
        
        # Variáveis para sensores de energia diária (daily_charge_kwh e daily_discharge_kwh)
        self._daily_energy = 0.0  # Acumulador de energia do dia
        self._last_power = 0.0  # Última potência registrada
        self._last_update = None  # Última atualização
        self._last_reset_date = None  # Data do último reset
        
        _LOGGER.debug(
            "Sensor %s initialized with nominal voltage: %.1f V",
            sensor_type, self._nominal_voltage
        )
        
        # Identificador único
        self._attr_unique_id = f"{device_id}_{sensor_type}"
        
        # Nome do sensor
        device_name = device_info.get("alias") or device_info.get("deviceSn", f"Battery {device_id}")
        self._attr_name = f"{device_name} {sensor_config['name']}"
        
        # Configurações do sensor
        self._attr_native_unit_of_measurement = sensor_config.get("unit")
        self._attr_icon = sensor_config.get("icon")
        self._attr_device_class = sensor_config.get("device_class")
        self._attr_state_class = sensor_config.get("state_class")

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_info.get("alias") or self._device_info.get("deviceSn", f"Battery {self._device_id}"),
            "manufacturer": "Felicity Solar",
            "model": self._device_info.get("deviceModel", "FSolar Battery"),
            "sw_version": self._device_info.get("moduleVersion") or self._device_info.get("ctVersion", "Unknown"),
        }

    async def async_added_to_hass(self) -> None:
        """Restore state when entity is added to hass."""
        await super().async_added_to_hass()
        
        # Restaurar estado para sensores de energia diária
        if self._sensor_type in ("daily_charge_kwh", "daily_discharge_kwh"):
            last_state = await self.async_get_last_state()
            if last_state and last_state.state not in (None, "unknown", "unavailable"):
                try:
                    self._daily_energy = float(last_state.state)
                    
                    # Restaurar atributos
                    if last_state.attributes:
                        if "last_reset_date" in last_state.attributes:
                            self._last_reset_date = last_state.attributes["last_reset_date"]
                        if "last_update" in last_state.attributes:
                            last_update_str = last_state.attributes["last_update"]
                            if last_update_str:
                                self._last_update = dt_util.parse_datetime(last_update_str)
                        if "last_power" in last_state.attributes:
                            self._last_power = float(last_state.attributes.get("last_power", 0))
                    
                    # Verificar se precisa resetar (mudou de dia)
                    today = dt_util.now().date().isoformat()
                    if self._last_reset_date != today:
                        _LOGGER.info(
                            "Device %s - New day detected for %s, resetting from %.3f kWh to 0",
                            self._device_id, self._sensor_type, self._daily_energy
                        )
                        self._daily_energy = 0.0
                        self._last_reset_date = today
                        self._last_power = 0.0
                        self._last_update = None
                    else:
                        _LOGGER.info(
                            "Device %s - Restored %s: %.3f kWh",
                            self._device_id, self._sensor_type, self._daily_energy
                        )
                except (ValueError, TypeError) as err:
                    _LOGGER.warning("Could not restore %s state: %s", self._sensor_type, err)
                    self._daily_energy = 0.0

    def _calculate_time_remaining(self, data: dict) -> float | None:
        """Calculate time remaining based on current state.
        
        Automatically detects if capacity is in Ah or kWh and converts accordingly.
        Priority: Current-based calculation > Power-based calculation
        """
        try:
            # Log de debug: mostrar todos os campos disponíveis
            _LOGGER.debug(
                "Device %s - Available data fields: %s",
                self._device_id,
                list(data.keys())
            )
            
            # Obter dados necessários
            soc = data.get("battSoc") or data.get("emsSoc")
            capacity_value = data.get("battCapacity") or data.get("emsCapacity") or data.get("totalEmsCapacity")
            charging_state = data.get("bmsChargingState")
            voltage = data.get("battVolt") or data.get("emsVoltage")
            
            # Log dos valores base
            _LOGGER.debug(
                "Device %s - Base data: SOC=%s, Capacity=%s, State=%s, Voltage=%s V",
                self._device_id, soc, capacity_value, charging_state, voltage
            )
            
            # Validar dados básicos
            if soc is None or capacity_value is None:
                _LOGGER.warning(
                    "Time remaining calculation failed for device %s: Missing SOC or capacity",
                    self._device_id
                )
                return None
            
            # Converter para float
            soc = float(soc)
            capacity_value = float(capacity_value)
            
            # CRÍTICO: Detectar se capacidade está em Ah ou kWh e converter
            # Heurística: valores > 50 provavelmente são Ah, valores <= 50 provavelmente são kWh
            if capacity_value > 50:
                # Provavelmente está em Ah, precisa converter para kWh
                if voltage:
                    voltage_float = float(voltage)
                    capacity_kwh = (capacity_value * voltage_float) / 1000
                    _LOGGER.info(
                        "Device %s - Detected capacity in Ah: %.1f Ah × %.1f V = %.2f kWh",
                        self._device_id, capacity_value, voltage_float, capacity_kwh
                    )
                else:
                    # Sem voltagem, assumir voltagem nominal de 25.6V (comum em baterias LiFePO4)
                    _LOGGER.warning(
                        "Device %s - No voltage data, assuming 25.6V nominal for conversion",
                        self._device_id
                    )
                    capacity_kwh = (capacity_value * 25.6) / 1000
                    _LOGGER.info(
                        "Device %s - Estimated capacity: %.1f Ah × 25.6 V = %.2f kWh",
                        self._device_id, capacity_value, capacity_kwh
                    )
            else:
                # Provavelmente já está em kWh
                capacity_kwh = capacity_value
                _LOGGER.debug(
                    "Device %s - Capacity appears to be in kWh: %.2f kWh",
                    self._device_id, capacity_kwh
                )
            
            # Se em standby, não há tempo de descarga/carga
            if charging_state == 0:
                _LOGGER.debug("Device %s in standby, no time calculation", self._device_id)
                return None
            
            # PRIORIDADE 1: Tentar cálculo por CORRENTE (mais preciso)
            if charging_state == 2:  # Descarregando
                # Tentar obter corrente de descarga
                discharge_current = (
                    data.get("batDisCurrent") or 
                    data.get("batDischargeCurrent") or
                    data.get("battCurr")  # Pode ser negativo durante descarga
                )
                
                if discharge_current:
                    current_a = abs(float(discharge_current))
                    if current_a > 0:
                        # Calcular capacidade disponível em Ah
                        voltage_for_calc = float(voltage) if voltage else 25.6
                        capacity_ah = (capacity_kwh * 1000) / voltage_for_calc
                        available_ah = (soc / 100) * capacity_ah
                        # Tempo restante em horas
                        time_remaining = available_ah / current_a
                        _LOGGER.info(
                            "Device %s - CURRENT calc (discharge): %.2f Ah / %.2f A = %.2f hours",
                            self._device_id, available_ah, current_a, time_remaining
                        )
                        return round(time_remaining, 2)
            
            elif charging_state == 1:  # Carregando
                # Tentar obter corrente de carga
                charge_current = (
                    data.get("batCharCurrent") or 
                    data.get("batChargeCurrent") or
                    data.get("battCurr")  # Pode ser positivo durante carga
                )
                
                if charge_current:
                    current_a = abs(float(charge_current))
                    if current_a > 0:
                        # Calcular capacidade necessária em Ah
                        voltage_for_calc = float(voltage) if voltage else 25.6
                        capacity_ah = (capacity_kwh * 1000) / voltage_for_calc
                        needed_ah = ((100 - soc) / 100) * capacity_ah
                        # Tempo até carga completa em horas
                        time_to_full = needed_ah / current_a
                        _LOGGER.info(
                            "Device %s - CURRENT calc (charge): %.2f Ah / %.2f A = %.2f hours",
                            self._device_id, needed_ah, current_a, time_to_full
                        )
                        return round(time_to_full, 2)
            
            # FALLBACK: Cálculo por POTÊNCIA
            _LOGGER.debug("Device %s - Current data not available, using power calculation", self._device_id)
            
            # Tentar múltiplos campos para potência de descarga
            discharging_power = (
                data.get("batDisPower") or 
                data.get("bmsPowerDischarge") or
                data.get("batDischargePower") or
                data.get("dischargingPower")
            )
            
            # Tentar múltiplos campos para potência de carga
            charging_power = (
                data.get("batCharPower") or 
                data.get("bmsPowerCharging") or 
                data.get("chargingPower") or
                data.get("batChargePower") or
                data.get("chargerPower")
            )
            
            # Log dos valores de potência encontrados
            _LOGGER.debug(
                "Device %s - Power data: charging_power=%s, discharging_power=%s",
                self._device_id, charging_power, discharging_power
            )
            
            # Se não encontrou potência específica, tentar usar bmsPower ou emsPower
            if not charging_power and not discharging_power:
                bms_power = data.get("bmsPower") or data.get("emsPower")
                _LOGGER.debug(
                    "Device %s - Trying fallback power fields: bmsPower=%s, emsPower=%s",
                    self._device_id, data.get("bmsPower"), data.get("emsPower")
                )
                
                if bms_power:
                    bms_power_float = float(bms_power)
                    if charging_state == 1 and bms_power_float != 0:
                        charging_power = abs(bms_power_float)
                        _LOGGER.info(
                            "Device %s - Using bmsPower/emsPower for charging: %s W",
                            self._device_id, charging_power
                        )
                    elif charging_state == 2 and bms_power_float != 0:
                        discharging_power = abs(bms_power_float)
                        _LOGGER.info(
                            "Device %s - Using bmsPower/emsPower for discharging: %s W",
                            self._device_id, discharging_power
                        )
            
            # Cálculo por potência
            if charging_state == 2:  # Descarregando
                if discharging_power and float(discharging_power) > 0:
                    power_w = float(discharging_power)
                    # Energia disponível em Wh
                    energy_available_wh = (soc / 100) * capacity_kwh * 1000
                    # Tempo restante em horas
                    time_remaining = energy_available_wh / power_w
                    _LOGGER.info(
                        "Device %s - POWER calc (discharge): %.2f Wh / %.2f W = %.2f hours",
                        self._device_id, energy_available_wh, power_w, time_remaining
                    )
                    return round(time_remaining, 2)
                else:
                    _LOGGER.warning(
                        "Device %s is discharging but no power data available",
                        self._device_id
                    )
            
            elif charging_state == 1:  # Carregando
                if charging_power and float(charging_power) > 0:
                    power_w = float(charging_power)
                    # Energia necessária para carregar completamente em Wh
                    energy_needed_wh = ((100 - soc) / 100) * capacity_kwh * 1000
                    # Tempo até carga completa em horas
                    time_to_full = energy_needed_wh / power_w
                    _LOGGER.info(
                        "Device %s - POWER calc (charge): %.2f Wh / %.2f W = %.2f hours",
                        self._device_id, energy_needed_wh, power_w, time_to_full
                    )
                    return round(time_to_full, 2)
                else:
                    _LOGGER.warning(
                        "Device %s is charging but no power data available. Data keys: %s",
                        self._device_id,
                        list(data.keys())
                    )
            
            return None
            
        except (ValueError, TypeError, ZeroDivisionError) as err:
            _LOGGER.error(
                "Error calculating time remaining for device %s: %s",
                self._device_id, err, exc_info=True
            )
            return None

    def _calculate_daily_energy(self, data: dict, charging: bool) -> float | None:
        """Calculate daily energy charged or discharged.
        
        Args:
            data: Battery data from API
            charging: True for charge sensor, False for discharge sensor
        
        Returns:
            Accumulated energy in kWh for today
        """
        try:
            now = dt_util.now()
            today = now.date().isoformat()
            
            # Verificar se mudou de dia (reset à meia-noite)
            if self._last_reset_date != today:
                _LOGGER.info(
                    "Device %s - New day for %s, resetting from %.3f kWh",
                    self._device_id, 
                    "charge" if charging else "discharge",
                    self._daily_energy
                )
                self._daily_energy = 0.0
                self._last_reset_date = today
                self._last_power = 0.0
                self._last_update = now
            
            # Obter potência atual
            if charging:
                # Potência de carga
                power = (
                    data.get("batCharPower") or 
                    data.get("bmsPowerCharging") or 
                    data.get("chargingPower") or
                    data.get("batChargePower") or
                    data.get("chargerPower")
                )
                
                # Fallback: usar bmsPower/emsPower se positivo
                if not power:
                    bms_power = data.get("bmsPower") or data.get("emsPower")
                    charging_state = data.get("bmsChargingState")
                    if bms_power and charging_state == 1:
                        power = abs(float(bms_power))
            else:
                # Potência de descarga
                power = (
                    data.get("batDisPower") or 
                    data.get("bmsPowerDischarge") or
                    data.get("batDischargePower") or
                    data.get("dischargingPower")
                )
                
                # Fallback: usar bmsPower/emsPower se negativo
                if not power:
                    bms_power = data.get("bmsPower") or data.get("emsPower")
                    charging_state = data.get("bmsChargingState")
                    if bms_power and charging_state == 2:
                        power = abs(float(bms_power))
            
            # Se não tem potência, retornar acumulado atual
            if not power:
                return round(self._daily_energy, 3)
            
            current_power = float(power)
            
            # Calcular energia desde última atualização
            if self._last_update and current_power > 0:
                # Tempo decorrido em horas
                time_delta = (now - self._last_update).total_seconds() / 3600
                
                # Energia = Potência média × Tempo
                # Usar média entre potência atual e anterior
                avg_power = (current_power + self._last_power) / 2
                energy_kwh = (avg_power * time_delta) / 1000
                
                # Acumular
                self._daily_energy += energy_kwh
                
                _LOGGER.debug(
                    "Device %s - %s: %.1f W × %.4f h = %.4f kWh (total: %.3f kWh)",
                    self._device_id,
                    "Charging" if charging else "Discharging",
                    avg_power,
                    time_delta,
                    energy_kwh,
                    self._daily_energy
                )
            
            # Atualizar estado para próxima iteração
            self._last_power = current_power
            self._last_update = now
            
            return round(self._daily_energy, 3)
            
        except (ValueError, TypeError) as err:
            _LOGGER.error(
                "Error calculating daily energy for device %s: %s",
                self._device_id, err
            )
            return round(self._daily_energy, 3) if self._daily_energy else 0.0

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self._device_id not in self.coordinator.data:
            return None

        device_data = self.coordinator.data[self._device_id]
        battery_data = device_data.get("battery_data", {})
        device_info = device_data.get("device_info", {})
        
        # Extrair dados do snapshot - a API retorna em data.data
        if isinstance(battery_data, dict):
            data = battery_data.get("data", battery_data)
        else:
            data = battery_data
        
        # Se for o sensor de tempo restante, calcular
        if self._sensor_type == "time_remaining":
            return self._calculate_time_remaining(data)
        
        # Se for o sensor de capacidade em kWh, calcular a partir de Ah
        if self._sensor_type == "battery_capacity_kwh":
            capacity_ah = data.get("battCapacity") or data.get("emsCapacity") or data.get("totalEmsCapacity")
            if capacity_ah:
                try:
                    capacity_ah_float = float(capacity_ah)
                    # Usar tensão nominal configurada
                    capacity_kwh = (capacity_ah_float * self._nominal_voltage) / 1000
                    _LOGGER.debug(
                        "Device %s - Calculating capacity kWh: %.1f Ah × %.1f V = %.2f kWh",
                        self._device_id, capacity_ah_float, self._nominal_voltage, capacity_kwh
                    )
                    return round(capacity_kwh, 2)
                except (ValueError, TypeError) as err:
                    _LOGGER.error("Error calculating battery_capacity_kwh: %s", err)
            return None
        
        # Se for o sensor de capacidade restante em kWh
        if self._sensor_type == "battery_remaining_kwh":
            capacity_ah = data.get("battCapacity") or data.get("emsCapacity") or data.get("totalEmsCapacity")
            soc = data.get("battSoc") or data.get("emsSoc")
            
            if capacity_ah and soc is not None:
                try:
                    capacity_ah_float = float(capacity_ah)
                    soc_float = float(soc)
                    
                    # Calcular capacidade total em kWh
                    capacity_kwh = (capacity_ah_float * self._nominal_voltage) / 1000
                    
                    # Calcular energia restante
                    remaining_kwh = (capacity_kwh * soc_float) / 100
                    
                    _LOGGER.debug(
                        "Device %s - Calculating remaining kWh: %.2f kWh × %.1f%% = %.2f kWh",
                        self._device_id, capacity_kwh, soc_float, remaining_kwh
                    )
                    return round(remaining_kwh, 2)
                except (ValueError, TypeError) as err:
                    _LOGGER.error("Error calculating battery_remaining_kwh: %s", err)
            return None
        
        # Se for sensor de carga diária
        if self._sensor_type == "daily_charge_kwh":
            return self._calculate_daily_energy(data, charging=True)
        
        # Se for sensor de descarga diária
        if self._sensor_type == "daily_discharge_kwh":
            return self._calculate_daily_energy(data, charging=False)
        
        # Mapear os dados da API FSolar para os sensores
        # Baseado na resposta real da API
        value_mapping = {
            # SOC e capacidade
            "battery_soc": data.get("battSoc") or data.get("emsSoc"),
            "battery_capacity": data.get("battCapacity") or data.get("emsCapacity") or data.get("totalEmsCapacity"),
            
            # Voltagem e corrente
            "battery_voltage": data.get("battVolt") or data.get("emsVoltage"),
            "battery_current": data.get("battCurr") or data.get("emsCurrent"),
            
            # Potência
            "battery_power": data.get("bmsPower") or data.get("emsPower"),
            
            # Temperatura
            "battery_temperature": data.get("tempMax") or data.get("tempMin"),
            
            # Potências de carga/descarga
            "charging_power": data.get("batCharPower") or data.get("bmsPowerCharging") or data.get("chargingPower"),
            "discharging_power": data.get("batDisPower") or data.get("bmsPowerDischarge"),
            
            # Totais de energia
            "total_charge": data.get("eBatCharTotal") or data.get("eBatCharToday") or data.get("bat1CharTotal"),
            "total_discharge": data.get("eBatDisCharTotal") or data.get("eBatDisCharToday") or data.get("bat1DisCharTotal"),
            
            # Saúde e ciclos
            "cycles": data.get("batCycleIndex") or data.get("batFullCount"),
            "health": data.get("battSoh") or data.get("emsSoh"),
            
            # Status de carga (novo)
            "charging_status": data.get("bmsChargingState"),
        }
        
        value = value_mapping.get(self._sensor_type)
        
        # Tratamento especial para charging_status (texto em vez de número)
        if self._sensor_type == "charging_status" and value is not None:
            return BATTERY_CHARGING_STATUS.get(int(value), "Unknown")
        
        # Converter valores se necessário
        if value is not None:
            try:
                # Remover valores inválidos como "3276.7" (temperatura placeholder)
                if isinstance(value, str):
                    val_float = float(value)
                    # Ignorar valores placeholder absurdos
                    if self._sensor_type == "battery_temperature" and val_float > 100:
                        return None
                    if val_float < -999 or val_float > 999999:
                        return None
                    return val_float
                elif isinstance(value, (int, float)):
                    return float(value)
            except (ValueError, TypeError):
                pass
        
        return value

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if self._device_id not in self.coordinator.data:
            return {}

        device_data = self.coordinator.data[self._device_id]
        battery_data = device_data.get("battery_data", {})
        device_info = device_data.get("device_info", {})
        
        # Extrair dados
        data = battery_data.get("data", battery_data) if isinstance(battery_data, dict) else battery_data
        
        attributes = {}
        
        # Adicionar status e informações gerais
        if self._sensor_type == "battery_soc":
            # Status do dispositivo
            device_status = device_info.get("status", "Unknown")
            attributes["device_status"] = DEVICE_STATUS.get(device_status, device_status)
            
            # Status de carga/descarga (bmsChargingState)
            charging_state = data.get("bmsChargingState")
            if charging_state is not None:
                attributes["charging_status"] = BATTERY_CHARGING_STATUS.get(charging_state, "Unknown")
                attributes["is_charging"] = charging_state == 1
                attributes["is_discharging"] = charging_state == 2
                attributes["is_standby"] = charging_state == 0
            
            attributes["bms_state"] = data.get("bmsState")
            attributes["last_update"] = data.get("dataTimeStr")
            attributes["plant_name"] = data.get("plantName") or device_info.get("plantName")
            attributes["device_model"] = data.get("deviceModel") or device_info.get("deviceModel")
            attributes["wifi_signal"] = data.get("wifiSignal")
            
        # Adicionar informações de temperatura
        if self._sensor_type == "battery_temperature":
            attributes["temp_max"] = data.get("tempMax")
            attributes["temp_min"] = data.get("tempMin")
            attributes["max_cell_temp_num"] = data.get("maxCellTempNum")
            attributes["min_cell_temp_num"] = data.get("minBattTempNum")
            
        # Adicionar informações de voltagem
        if self._sensor_type == "battery_voltage":
            attributes["max_voltage"] = data.get("maxVoltage2bms")
            attributes["min_voltage"] = data.get("minVoltage2bms")
            attributes["max_voltage_cell"] = data.get("maxVoltageNum2bms")
            attributes["min_voltage_cell"] = data.get("minVoltageNum2bms")
            attributes["bms_lc_volt"] = data.get("BMSLCVolt")
            attributes["bms_ld_volt"] = data.get("BMSLDVolt")
        
        # Adicionar informações de capacidade
        if self._sensor_type == "battery_capacity":
            voltage = data.get("battVolt") or data.get("emsVoltage")
            if voltage:
                attributes["voltage_v"] = float(voltage)
            
            # Adicionar outras capacidades disponíveis
            if data.get("emsCapacity"):
                attributes["ems_capacity_ah"] = data.get("emsCapacity")
            if data.get("ratedEnergy"):
                attributes["rated_energy_wh"] = data.get("ratedEnergy")
        
        # Adicionar informações de capacidade em kWh
        if self._sensor_type == "battery_capacity_kwh":
            capacity_ah = data.get("battCapacity") or data.get("emsCapacity") or data.get("totalEmsCapacity")
            if capacity_ah:
                attributes["capacity_ah"] = float(capacity_ah)
            
            attributes["nominal_voltage_v"] = self._nominal_voltage
            
            # Voltagem real atual (se disponível)
            voltage = data.get("battVolt") or data.get("emsVoltage")
            if voltage:
                attributes["current_voltage_v"] = float(voltage)
            
            # Mostrar outras capacidades
            if data.get("emsCapacity"):
                attributes["ems_capacity_ah"] = data.get("emsCapacity")
            if data.get("ratedEnergy"):
                attributes["rated_energy_wh"] = data.get("ratedEnergy")
        
        # Adicionar informações de capacidade restante em kWh
        if self._sensor_type == "battery_remaining_kwh":
            capacity_ah = data.get("battCapacity") or data.get("emsCapacity") or data.get("totalEmsCapacity")
            soc = data.get("battSoc") or data.get("emsSoc")
            
            if capacity_ah:
                capacity_ah_float = float(capacity_ah)
                capacity_kwh = (capacity_ah_float * self._nominal_voltage) / 1000
                attributes["capacity_ah"] = capacity_ah_float
                attributes["total_capacity_kwh"] = round(capacity_kwh, 2)
            
            if soc is not None:
                attributes["current_soc"] = float(soc)
            
            attributes["nominal_voltage_v"] = self._nominal_voltage
            
            # Voltagem real atual
            voltage = data.get("battVolt") or data.get("emsVoltage")
            if voltage:
                attributes["current_voltage_v"] = float(voltage)
            
            # Status de carga/descarga
            charging_state = data.get("bmsChargingState")
            if charging_state is not None:
                attributes["charging_status"] = BATTERY_CHARGING_STATUS.get(charging_state, "Unknown")
            
        # Adicionar informações de potência
        if self._sensor_type in ["battery_power", "charging_power", "discharging_power"]:
            # Status de carga/descarga
            charging_state = data.get("bmsChargingState")
            if charging_state is not None:
                attributes["charging_status"] = BATTERY_CHARGING_STATUS.get(charging_state, "Unknown")
                attributes["is_charging"] = charging_state == 1
                attributes["is_discharging"] = charging_state == 2
                attributes["is_standby"] = charging_state == 0
            
            attributes["bat_char_current"] = data.get("batCharCurrent")
            attributes["bat_dis_current"] = data.get("batDisCurrent")
            attributes["bat_char_power"] = data.get("batCharPower")
            attributes["bat_dis_power"] = data.get("batDisPower")
            
        # Adicionar informações de saúde
        if self._sensor_type == "health":
            attributes["battery_capacity"] = data.get("battCapacity")
            attributes["ems_capacity"] = data.get("emsCapacity")
            attributes["rated_energy"] = data.get("ratedEnergy")
            attributes["cycles"] = data.get("batCycleIndex")
        
        # Adicionar atributos dos sensores de energia diária
        if self._sensor_type in ("daily_charge_kwh", "daily_discharge_kwh"):
            # Data do último reset
            if self._last_reset_date:
                attributes["last_reset_date"] = self._last_reset_date
            
            # Última atualização
            if self._last_update:
                attributes["last_update"] = self._last_update.isoformat()
            
            # Potência atual
            if self._last_power:
                attributes["last_power"] = round(self._last_power, 1)
            
            # Status de carga/descarga
            charging_state = data.get("bmsChargingState")
            if charging_state is not None:
                attributes["charging_status"] = BATTERY_CHARGING_STATUS.get(charging_state, "Unknown")
                attributes["is_active"] = (
                    charging_state == 1 if self._sensor_type == "daily_charge_kwh" 
                    else charging_state == 2
                )
        
        # Adicionar detalhes do cálculo de tempo restante
        if self._sensor_type == "time_remaining":
            charging_state = data.get("bmsChargingState")
            if charging_state is not None:
                attributes["charging_status"] = BATTERY_CHARGING_STATUS.get(charging_state, "Unknown")
                attributes["is_charging"] = charging_state == 1
                attributes["is_discharging"] = charging_state == 2
                attributes["is_standby"] = charging_state == 0
            
            # Adicionar dados usados no cálculo
            soc = data.get("battSoc") or data.get("emsSoc")
            capacity_value = data.get("battCapacity") or data.get("emsCapacity")
            voltage = data.get("battVolt") or data.get("emsVoltage")
            
            if soc is not None:
                attributes["current_soc"] = float(soc)
            
            # CONVERTER capacidade de Ah para kWh se necessário
            if capacity_value is not None:
                capacity_float = float(capacity_value)
                if capacity_float > 50:  # Provavelmente em Ah
                    if voltage:
                        voltage_float = float(voltage)
                        capacity_kwh = (capacity_float * voltage_float) / 1000
                        attributes["battery_capacity_ah"] = capacity_float
                        attributes["battery_capacity_kwh"] = round(capacity_kwh, 2)
                        attributes["battery_voltage_v"] = voltage_float
                    else:
                        # Assumir 25.6V se voltagem não disponível
                        capacity_kwh = (capacity_float * 25.6) / 1000
                        attributes["battery_capacity_ah"] = capacity_float
                        attributes["battery_capacity_kwh"] = round(capacity_kwh, 2)
                        attributes["battery_voltage_v"] = 25.6
                        attributes["voltage_assumed"] = True
                else:
                    # Já está em kWh
                    attributes["battery_capacity_kwh"] = capacity_float
                
                # Usar a capacidade convertida para os cálculos
                capacity_for_calc = capacity_kwh if capacity_float > 50 else capacity_float
            else:
                capacity_for_calc = None
            
            # Adicionar potência atual com múltiplas tentativas
            if charging_state == 2:  # Descarregando
                power = (
                    data.get("batDisPower") or 
                    data.get("bmsPowerDischarge") or
                    data.get("batDischargePower") or
                    data.get("dischargingPower")
                )
                # Se não encontrou, tentar bmsPower/emsPower e usar valor absoluto
                if not power:
                    bms_power = data.get("bmsPower") or data.get("emsPower")
                    if bms_power:
                        power = abs(float(bms_power))
                
                if power:
                    attributes["current_power_w"] = float(power)
                    # Calcular energia disponível (usando capacidade convertida)
                    if soc and capacity_for_calc:
                        energy_available = (float(soc) / 100) * capacity_for_calc
                        attributes["energy_available_kwh"] = round(energy_available, 2)
                else:
                    # Adicionar debug info se não encontrou potência
                    attributes["debug_no_power"] = "No discharging power field found in API data"
                    
            elif charging_state == 1:  # Carregando
                power = (
                    data.get("batCharPower") or 
                    data.get("bmsPowerCharging") or 
                    data.get("chargingPower") or
                    data.get("batChargePower") or
                    data.get("chargerPower")
                )
                # Se não encontrou, tentar bmsPower/emsPower e usar valor absoluto
                if not power:
                    bms_power = data.get("bmsPower") or data.get("emsPower")
                    if bms_power:
                        power = abs(float(bms_power))
                
                if power:
                    attributes["current_power_w"] = float(power)
                    # Calcular energia necessária (usando capacidade convertida)
                    if soc and capacity_for_calc:
                        energy_needed = ((100 - float(soc)) / 100) * capacity_for_calc
                        attributes["energy_needed_kwh"] = round(energy_needed, 2)
                else:
                    # Adicionar debug info se não encontrou potência
                    attributes["debug_no_power"] = "No charging power field found in API data"
            
            
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self._device_id in self.coordinator.data
        )

    @property
    def icon(self) -> str | None:
        """Return the icon to use based on state."""
        # Ícone dinâmico para o sensor de tempo restante
        if self._sensor_type == "time_remaining":
            if self._device_id in self.coordinator.data:
                device_data = self.coordinator.data[self._device_id]
                battery_data = device_data.get("battery_data", {})
                data = battery_data.get("data", battery_data) if isinstance(battery_data, dict) else battery_data
                
                charging_state = data.get("bmsChargingState")
                if charging_state == 1:  # Carregando
                    return "mdi:battery-charging"
                elif charging_state == 2:  # Descarregando
                    return "mdi:battery-arrow-down"
                else:  # Standby
                    return "mdi:battery-clock"
        
        # Usar ícone padrão do sensor
        return self._attr_icon
