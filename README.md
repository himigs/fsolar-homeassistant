# FSolar Plugin - Versão com Tempo Restante

## 🆕 Nova Funcionalidade: Contador de Tempo Restante

Esta versão modificada do plugin FSolar adiciona um novo sensor que calcula o tempo restante da bateria com base no estado atual de carga, capacidade e consumo/carregamento.

## ⏱️ Sensor de Tempo Restante

### O que ele faz?

O sensor **"Time Remaining"** calcula automaticamente:

- **Durante descarga**: Quanto tempo falta para a bateria descarregar completamente
- **Durante carga**: Quanto tempo falta para a bateria carregar completamente
- **Em standby**: Não exibe valor (bateria parada)

### Como funciona?

O cálculo é feito usando a seguinte lógica:

#### Descarga (Discharging)
```
Tempo Restante (horas) = (SOC% × Capacidade kWh × 1000) ÷ Potência de Descarga (W)
```

**Exemplo:**
- SOC: 80%
- Capacidade: 10 kWh
- Potência de descarga: 2000 W

```
Tempo = (80% × 10 kWh × 1000) ÷ 2000 W = 4 horas
```

#### Carga (Charging)
```
Tempo até Cheio (horas) = ((100 - SOC%) × Capacidade kWh × 1000) ÷ Potência de Carga (W)
```

**Exemplo:**
- SOC: 30%
- Capacidade: 10 kWh
- Potência de carga: 3000 W

```
Tempo = ((100 - 30)% × 10 kWh × 1000) ÷ 3000 W = 2.33 horas
```

## 📊 Atributos Adicionais

O sensor de tempo restante também fornece atributos extras:

- `charging_status`: Status atual (Standby/Charging/Discharging)
- `is_charging`: Verdadeiro se estiver carregando
- `is_discharging`: Verdadeiro se estiver descarregando
- `is_standby`: Verdadeiro se estiver parada
- `current_soc`: SOC atual em %
- `battery_capacity_kwh`: Capacidade da bateria em kWh
- `current_power_w`: Potência atual em Watts
- `energy_available_kwh`: Energia disponível (durante descarga)
- `energy_needed_kwh`: Energia necessária para carga completa (durante carga)

## 🎨 Ícone Dinâmico

O sensor muda o ícone automaticamente baseado no estado:
- 🔋⚡ Carregando: `mdi:battery-charging`
- 🔋⬇️ Descarregando: `mdi:battery-arrow-down`
- 🔋🕐 Standby: `mdi:battery-clock`

## 📦 Instalação

1. Substitua a pasta `fsolar` no seu diretório `custom_components` pela pasta `fsolar_modified`
2. Renomeie `fsolar_modified` para `fsolar`
3. Reinicie o Home Assistant
4. O novo sensor "Time Remaining" aparecerá automaticamente para cada bateria

## 🔍 Exemplo de Uso no Home Assistant

### Card de Entity
```yaml
type: entity
entity: sensor.battery_12345_time_remaining
name: Tempo Restante da Bateria
icon: mdi:timer-outline
```

### Card de Entities com Detalhes
```yaml
type: entities
title: Status da Bateria
entities:
  - entity: sensor.battery_12345_battery_soc
    name: Carga
  - entity: sensor.battery_12345_charging_status
    name: Status
  - entity: sensor.battery_12345_battery_power
    name: Potência Atual
  - entity: sensor.battery_12345_time_remaining
    name: Tempo Restante
    secondary_info: last-changed
```

### Automação de Alerta
```yaml
automation:
  - alias: "Aviso: Bateria Baixa"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_12345_time_remaining
        below: 0.5  # Menos de 30 minutos
    condition:
      - condition: state
        entity_id: sensor.battery_12345_charging_status
        state: "Discharging"
    action:
      - service: notify.mobile_app
        data:
          title: "Bateria Baixa"
          message: "A bateria tem menos de 30 minutos de carga restante!"
```

## 📝 Notas Técnicas

### Dados Necessários
O sensor precisa dos seguintes dados da API FSolar:
- `battSoc` ou `emsSoc`: Estado de carga em %
- `battCapacity`, `emsCapacity` ou `totalEmsCapacity`: Capacidade em kWh
- `bmsChargingState`: Estado de carga (0=Standby, 1=Charging, 2=Discharging)
- `batDisPower` ou `bmsPowerDischarge`: Potência de descarga em W
- `batCharPower`, `bmsPowerCharging` ou `chargingPower`: Potência de carga em W

### Limitações
- O cálculo assume consumo/carga constante
- Não considera eficiência de carga/descarga
- Valores podem variar com mudanças na carga
- Retorna `None` quando em standby ou quando dados estão indisponíveis

## 🆚 Comparação com Versão Original

| Recurso | Versão Original | Versão Modificada |
|---------|----------------|-------------------|
| SOC (%) | ✅ | ✅ |
| Voltagem | ✅ | ✅ |
| Corrente | ✅ | ✅ |
| Potência | ✅ | ✅ |
| Temperatura | ✅ | ✅ |
| Capacidade | ✅ | ✅ |
| Ciclos | ✅ | ✅ |
| Saúde | ✅ | ✅ |
| Status de Carga | ✅ | ✅ |
| **Tempo Restante** | ❌ | ✅ **NOVO** |
| **Ícone Dinâmico** | ❌ | ✅ **NOVO** |
| **Atributos Extras** | ❌ | ✅ **NOVO** |

## 🐛 Troubleshooting

### O sensor mostra "Unknown" ou "Unavailable"
- Verifique se a bateria está realmente carregando ou descarregando
- Confirme se a API está retornando dados de potência
- Confira os logs do Home Assistant para erros

### O tempo não parece preciso
- O cálculo é baseado no consumo/carga **atual**
- Valores flutuam conforme o uso muda
- É uma **estimativa**, não uma previsão exata

### O sensor não aparece
- Reinicie o Home Assistant completamente
- Verifique se os arquivos foram copiados corretamente
- Confirme que não há erros nos logs

## 📄 Arquivos Modificados

- `const.py`: Adicionado novo sensor type "time_remaining"
- `sensor.py`: Implementada função `_calculate_time_remaining()` e lógica de ícone dinâmico

## ✨ Créditos

Modificação adicionada por: Claude (Anthropic)
Plugin original: FSolar Battery Integration for Home Assistant
