# Exemplos de Uso - FSolar Time Remaining

## 📊 Cards para Dashboard

### 1. Card Simples com Tempo Restante

```yaml
type: entity
entity: sensor.battery_12345_time_remaining
name: Tempo Restante
icon: mdi:timer-outline
```

### 2. Card Gauge (Medidor)

```yaml
type: gauge
entity: sensor.battery_12345_time_remaining
name: Tempo Restante
min: 0
max: 10
severity:
  green: 3
  yellow: 1
  red: 0
```

### 3. Card Completo com Múltiplos Sensores

```yaml
type: entities
title: Status Completo da Bateria
entities:
  - type: section
    label: Estado
  - entity: sensor.battery_12345_battery_soc
    name: Carga da Bateria
    icon: mdi:battery
  - entity: sensor.battery_12345_charging_status
    name: Status
  - entity: sensor.battery_12345_time_remaining
    name: Tempo Restante
    icon: mdi:timer-outline
  
  - type: section
    label: Potência
  - entity: sensor.battery_12345_battery_power
    name: Potência Atual
  - entity: sensor.battery_12345_battery_voltage
    name: Voltagem
  - entity: sensor.battery_12345_battery_current
    name: Corrente
  
  - type: section
    label: Saúde
  - entity: sensor.battery_12345_health
    name: Saúde da Bateria
  - entity: sensor.battery_12345_cycles
    name: Ciclos
  - entity: sensor.battery_12345_battery_temperature
    name: Temperatura
```

### 4. Card de Estatísticas

```yaml
type: statistic
entity: sensor.battery_12345_time_remaining
name: Histórico Tempo Restante
period:
  calendar:
    period: day
stat_types:
  - mean
  - min
  - max
```

### 5. Card Condicional (Só Mostra Durante Descarga)

```yaml
type: conditional
conditions:
  - entity: sensor.battery_12345_charging_status
    state: "Discharging"
card:
  type: entity
  entity: sensor.battery_12345_time_remaining
  name: ⚠️ Tempo até Descarga Completa
  icon: mdi:battery-alert
```

## 🤖 Automações

### 1. Notificação - Bateria Quase Vazia (30 min)

```yaml
automation:
  - alias: "Aviso: Bateria com 30 minutos restantes"
    description: "Notifica quando resta apenas 30 minutos de carga"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_12345_time_remaining
        below: 0.5  # 0.5 horas = 30 minutos
    condition:
      - condition: state
        entity_id: sensor.battery_12345_charging_status
        state: "Discharging"
      - condition: numeric_state
        entity_id: sensor.battery_12345_battery_soc
        above: 10  # Evita notificações quando já está muito baixa
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Bateria Baixa"
          message: "A bateria tem apenas {{ states('sensor.battery_12345_time_remaining') | round(1) }} horas restantes!"
          data:
            priority: high
            ttl: 0
```

### 2. Notificação - Bateria Crítica (10 min)

```yaml
automation:
  - alias: "CRÍTICO: Bateria com 10 minutos"
    description: "Alerta crítico quando faltam 10 minutos"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_12345_time_remaining
        below: 0.17  # 0.17 horas ≈ 10 minutos
    condition:
      - condition: state
        entity_id: sensor.battery_12345_charging_status
        state: "Discharging"
    action:
      - service: notify.mobile_app
        data:
          title: "🚨 BATERIA CRÍTICA"
          message: "Faltam menos de 10 minutos de carga!"
          data:
            priority: high
            ttl: 0
            channel: alarm_stream
      - service: light.turn_on
        target:
          entity_id: light.sala
        data:
          rgb_color: [255, 0, 0]
          brightness: 255
          flash: long
```

### 3. Ligar Carregamento Quando Baixo

```yaml
automation:
  - alias: "Iniciar carregamento automático"
    description: "Inicia carregamento quando tempo restante é baixo"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_12345_time_remaining
        below: 1  # 1 hora
    condition:
      - condition: state
        entity_id: sensor.battery_12345_charging_status
        state: "Discharging"
      - condition: numeric_state
        entity_id: sensor.battery_12345_battery_soc
        below: 30
      - condition: time
        after: "18:00:00"
        before: "23:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.battery_charger
      - service: notify.mobile_app
        data:
          title: "🔌 Carregamento Iniciado"
          message: "Bateria baixa detectada, iniciando carregamento automático"
```

### 4. Notificar Quando Carga Completa Próxima

```yaml
automation:
  - alias: "Bateria quase cheia"
    description: "Notifica quando faltam 30 min para carga completa"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_12345_time_remaining
        below: 0.5
    condition:
      - condition: state
        entity_id: sensor.battery_12345_charging_status
        state: "Charging"
    action:
      - service: notify.mobile_app
        data:
          title: "✅ Carga Quase Completa"
          message: "A bateria estará totalmente carregada em aproximadamente {{ states('sensor.battery_12345_time_remaining') | round(1) }} horas"
```

### 5. Relatório Diário

```yaml
automation:
  - alias: "Relatório diário da bateria"
    description: "Envia relatório diário sobre uso da bateria"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "📊 Relatório Diário - Bateria"
          message: >
            Carga atual: {{ states('sensor.battery_12345_battery_soc') }}%
            Status: {{ states('sensor.battery_12345_charging_status') }}
            {% if states('sensor.battery_12345_charging_status') == 'Discharging' %}
            Tempo restante: {{ states('sensor.battery_12345_time_remaining') | round(1) }} horas
            {% elif states('sensor.battery_12345_charging_status') == 'Charging' %}
            Tempo até completa: {{ states('sensor.battery_12345_time_remaining') | round(1) }} horas
            {% endif %}
            Saúde: {{ states('sensor.battery_12345_health') }}%
            Ciclos: {{ states('sensor.battery_12345_cycles') }}
```

## 📈 Gráficos e História

### 1. Card de Histórico

```yaml
type: history-graph
title: Histórico de Tempo Restante
entities:
  - entity: sensor.battery_12345_time_remaining
    name: Tempo Restante
  - entity: sensor.battery_12345_battery_soc
    name: SOC
hours_to_show: 24
refresh_interval: 0
```

### 2. Card Apex Charts (requer custom card)

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Tempo Restante vs SOC
span:
  start: day
graph_span: 24h
series:
  - entity: sensor.battery_12345_time_remaining
    name: Tempo Restante (h)
    yaxis_id: time
    stroke_width: 2
    color: blue
  - entity: sensor.battery_12345_battery_soc
    name: SOC (%)
    yaxis_id: soc
    stroke_width: 2
    color: green
yaxis:
  - id: time
    decimals: 1
    apex_config:
      tickAmount: 5
  - id: soc
    opposite: true
    decimals: 0
    max: 100
```

## 🎯 Scripts Úteis

### 1. Script para Economizar Bateria

```yaml
script:
  battery_saving_mode:
    alias: "Modo Economia de Bateria"
    sequence:
      - service: notify.mobile_app
        data:
          title: "🔋 Modo Economia Ativado"
          message: "Desligando dispositivos não essenciais"
      - service: light.turn_off
        target:
          entity_id: 
            - light.sala
            - light.quarto
      - service: climate.turn_off
        target:
          entity_id: climate.ar_condicionado
      - service: switch.turn_off
        target:
          entity_id: switch.tv
```

### 2. Script para Verificar Status

```yaml
script:
  check_battery_status:
    alias: "Verificar Status da Bateria"
    sequence:
      - service: notify.mobile_app
        data:
          title: "📊 Status da Bateria"
          message: >
            Carga: {{ states('sensor.battery_12345_battery_soc') }}%
            Status: {{ states('sensor.battery_12345_charging_status') }}
            Tempo restante: {{ states('sensor.battery_12345_time_remaining') | round(1) }} h
            Potência: {{ states('sensor.battery_12345_battery_power') }} W
            Temperatura: {{ states('sensor.battery_12345_battery_temperature') }}°C
```

## 🎨 Lovelace Dashboard Completo

```yaml
type: vertical-stack
cards:
  # Cabeçalho
  - type: markdown
    content: |
      # 🔋 Bateria FSolar
      Status atualizado: {{ as_timestamp(states.sensor.battery_12345_battery_soc.last_changed) | timestamp_custom('%H:%M:%S') }}
  
  # Indicador principal
  - type: horizontal-stack
    cards:
      - type: gauge
        entity: sensor.battery_12345_battery_soc
        name: Carga
        min: 0
        max: 100
        severity:
          green: 60
          yellow: 30
          red: 0
      
      - type: entity
        entity: sensor.battery_12345_time_remaining
        name: Tempo Restante
        icon: mdi:timer-outline
  
  # Status detalhado
  - type: entities
    entities:
      - entity: sensor.battery_12345_charging_status
        name: Status
      - entity: sensor.battery_12345_battery_power
        name: Potência
      - entity: sensor.battery_12345_battery_voltage
        name: Voltagem
      - entity: sensor.battery_12345_battery_temperature
        name: Temperatura
  
  # Saúde
  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.battery_12345_health
        name: Saúde
      - type: entity
        entity: sensor.battery_12345_cycles
        name: Ciclos
  
  # Gráfico
  - type: history-graph
    entities:
      - sensor.battery_12345_battery_soc
      - sensor.battery_12345_time_remaining
    hours_to_show: 12
```

## 💡 Dicas

1. **Ajuste os IDs**: Substitua `battery_12345` pelo ID real da sua bateria
2. **Teste as automações**: Ajuste os valores de trigger de acordo com suas necessidades
3. **Personalização**: Modifique cores, ícones e mensagens conforme preferir
4. **Notificações**: Configure o serviço de notificação correto (mobile_app, telegram, etc)
5. **Backup**: Sempre faça backup antes de modificar configurações

## 🔧 Personalização Avançada

### Template Sensor para Minutos

Se preferir ver o tempo em minutos:

```yaml
template:
  - sensor:
      - name: "Battery Time Remaining Minutes"
        unique_id: battery_time_remaining_minutes
        unit_of_measurement: "min"
        state: >
          {% set hours = states('sensor.battery_12345_time_remaining') | float(0) %}
          {{ (hours * 60) | round(0) }}
        icon: mdi:timer
```

### Template para Tempo Formatado

Para exibir como "2h 30min":

```yaml
template:
  - sensor:
      - name: "Battery Time Formatted"
        unique_id: battery_time_formatted
        state: >
          {% set time = states('sensor.battery_12345_time_remaining') | float(0) %}
          {% set hours = time | int %}
          {% set minutes = ((time - hours) * 60) | int %}
          {{ hours }}h {{ minutes }}min
        icon: mdi:timer
```
