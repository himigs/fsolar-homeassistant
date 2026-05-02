# Exemplos de Uso - FSolar Integration

> **⚠️ Nota de Versão (v2.1.0+):** O sensor `time_remaining` foi separado em dois sensores distintos:
> - `time_to_empty` — ativo apenas durante a **descarga** (retorna *Indisponível* durante carga/standby)
> - `time_to_full` — ativo apenas durante a **carga** (retorna *Indisponível* durante descarga/standby)
>
> **Vantagem:** Suas automações **não precisam mais verificar o `charging_status`**. Basta usar o valor numérico diretamente!

---

## 📊 Cards para Dashboard

### 1. Card Simples - Tempo para Descarregar

```yaml
type: entity
entity: sensor.battery_12345_time_to_empty
name: Tempo até Descarregar
icon: mdi:battery-arrow-down
```

### 2. Card Simples - Tempo para Carregar

```yaml
type: entity
entity: sensor.battery_12345_time_to_full
name: Tempo até Carga Completa
icon: mdi:battery-charging
```

### 3. Card Gauge - Autonomia Restante

```yaml
type: gauge
entity: sensor.battery_12345_time_to_empty
name: Autonomia Restante
min: 0
max: 10
severity:
  green: 3
  yellow: 1
  red: 0
```

### 4. Card Completo com Múltiplos Sensores

```yaml
type: entities
title: Status Completo da Bateria
entities:
  - type: section
    label: Estado
  - entity: sensor.battery_12345_battery_soc
    name: Carga da Bateria
  - entity: sensor.battery_12345_charging_status
    name: Status
  - entity: sensor.battery_12345_time_to_empty
    name: Tempo até Descarregar
  - entity: sensor.battery_12345_time_to_full
    name: Tempo até Carregar

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

### 5. Card Condicional - Só Mostra Durante Descarga

```yaml
type: conditional
conditions:
  - entity: sensor.battery_12345_time_to_empty
    state_not: unavailable
card:
  type: entity
  entity: sensor.battery_12345_time_to_empty
  name: ⚠️ Tempo até Descarga Completa
  icon: mdi:battery-alert
```

---

## 🤖 Automações

> **Dica:** Como os sensores retornam `None`/Indisponível quando inativos, **não é necessário checar o `charging_status`** nas condições. O HA ignora comparações numéricas com sensores indisponíveis.

### 1. Notificação - Bateria Quase Vazia (30 min)

```yaml
automation:
  - alias: "Aviso: Bateria com 30 minutos restantes"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_12345_time_to_empty
        below: 0.5  # 0.5 horas = 30 minutos
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Bateria Baixa"
          message: >
            A bateria tem apenas
            {{ states('sensor.battery_12345_time_to_empty') | round(1) }} horas restantes!
```

### 2. Alerta Crítico - 10 Minutos Restantes

```yaml
automation:
  - alias: "CRÍTICO: Bateria com 10 minutos"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_12345_time_to_empty
        below: 0.17  # ≈ 10 minutos
    action:
      - service: notify.mobile_app
        data:
          title: "🚨 BATERIA CRÍTICA"
          message: "Faltam menos de 10 minutos de carga!"
          data:
            priority: high
            channel: alarm_stream
```

### 3. Notificar Quando Carga Completa Próxima

```yaml
automation:
  - alias: "Bateria quase cheia"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_12345_time_to_full
        below: 0.5  # 30 minutos
    action:
      - service: notify.mobile_app
        data:
          title: "✅ Carga Quase Completa"
          message: >
            A bateria estará totalmente carregada em
            {{ states('sensor.battery_12345_time_to_full') | round(1) }} horas.
```

### 4. Relatório Diário

```yaml
automation:
  - alias: "Relatório diário da bateria"
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
            {% if states('sensor.battery_12345_time_to_empty') not in ['unavailable','unknown'] %}
            Autonomia restante: {{ states('sensor.battery_12345_time_to_empty') | round(1) }} horas
            {% elif states('sensor.battery_12345_time_to_full') not in ['unavailable','unknown'] %}
            Tempo até carga completa: {{ states('sensor.battery_12345_time_to_full') | round(1) }} horas
            {% endif %}
            Saúde: {{ states('sensor.battery_12345_health') }}%
            Ciclos: {{ states('sensor.battery_12345_cycles') }}
```

---

## 📈 Gráficos e História

### 1. Card de Histórico

```yaml
type: history-graph
title: Autonomia da Bateria
entities:
  - entity: sensor.battery_12345_time_to_empty
    name: Tempo até Descarregar
  - entity: sensor.battery_12345_time_to_full
    name: Tempo até Carregar
  - entity: sensor.battery_12345_battery_soc
    name: SOC
hours_to_show: 24
```

> **Nota sobre gaps no gráfico:** Quando `time_to_empty` está *Indisponível* (durante a carga), o gráfico exibirá um intervalo vazio. Esse comportamento é intencional e informativo — você consegue ver visualmente quando a bateria estava carregando vs. descarregando.

### 2. ApexCharts (requer custom card)

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Autonomia vs SOC
graph_span: 24h
series:
  - entity: sensor.battery_12345_time_to_empty
    name: Tempo até Descarregar (h)
    yaxis_id: time
    color: "#f44336"
  - entity: sensor.battery_12345_time_to_full
    name: Tempo até Carregar (h)
    yaxis_id: time
    color: "#4caf50"
  - entity: sensor.battery_12345_battery_soc
    name: SOC (%)
    yaxis_id: soc
    color: "#2196f3"
yaxis:
  - id: time
    decimals: 1
  - id: soc
    opposite: true
    max: 100
```

---

## 🎨 Dashboard Completo

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      # 🔋 Bateria FSolar
      Atualizado: {{ as_timestamp(states.sensor.battery_12345_battery_soc.last_changed) | timestamp_custom('%H:%M:%S') }}

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
        entity: sensor.battery_12345_time_to_empty
        name: Autonomia Restante
      - type: entity
        entity: sensor.battery_12345_time_to_full
        name: Tempo p/ Carregar

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

  - type: history-graph
    entities:
      - sensor.battery_12345_battery_soc
      - sensor.battery_12345_time_to_empty
      - sensor.battery_12345_time_to_full
    hours_to_show: 12
```

---

## 💡 Dicas

1. **Substitua o ID**: Troque `battery_12345` pelo ID real da sua bateria.
2. **Sem condição de status**: Com os novos sensores, não é mais necessário checar `charging_status` nas automações de tempo.
3. **Template em minutos** (sensor auxiliar):

```yaml
template:
  - sensor:
      - name: "Autonomia em Minutos"
        unit_of_measurement: "min"
        state: >
          {% set h = states('sensor.battery_12345_time_to_empty') | float(-1) %}
          {{ (h * 60) | round(0) if h >= 0 else 'unavailable' }}
```
