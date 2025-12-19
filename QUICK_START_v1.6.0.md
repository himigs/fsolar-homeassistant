# ⚡ Resumo Rápido - Versão 1.6.0

## 🆕 Dois Novos Sensores para Energy Dashboard!

### Energia Diária - Acumula e Reseta Automaticamente

#### 1. daily_charge_kwh 🔌
```yaml
sensor.daily_charge_kwh:
  state: 6.50 kWh              # Total carregado hoje
```

#### 2. daily_discharge_kwh 🔋
```yaml
sensor.daily_discharge_kwh:
  state: 2.00 kWh              # Total descarregado hoje
```

## 🎯 Para Energy Dashboard

### Configuração Rápida

```
1. Configurações → Dashboards → Energia
2. Armazenamento de Bateria:
   ✅ Entrada: sensor.daily_charge_kwh
   ✅ Saída: sensor.daily_discharge_kwh
3. Salvar
```

### Resultado

```
Energy Dashboard mostrará:
├─ Energia Carregada: 6.50 kWh  🔌
├─ Energia Descarregada: 2.00 kWh  🔋
└─ Balanço: +4.50 kWh  ✅
```

## 🧮 Como Funciona

```
Energia = Potência × Tempo

Exemplo:
10:00 - Carga 1000W
11:00 - 1000W × 1h = 1.00 kWh (acumula)
12:00 - 1200W × 1h = 1.20 kWh (acumula)
Total: 2.20 kWh

00:00 - RESET para 0  🔄
```

## ⏰ Reset Automático

✅ À meia-noite (00:00) ambos sensores resetam  
✅ Começa novo dia do zero  
✅ Histórico salvo no banco de dados  

## 💾 Persiste Entre Reinícios

✅ Sobrevive a reinícios do Home Assistant  
✅ Sobrevive a quedas de energia  
✅ Estado é restaurado automaticamente  

## 📊 Todos os Sensores Agora

| Sensor | Mostra | Atualiza |
|--------|--------|----------|
| battery_capacity | 100 Ah | - |
| battery_capacity_kwh | 2.56 kWh | - |
| battery_remaining_kwh | 1.08 kWh | Tempo real |
| battery_soc | 42% | Tempo real |
| time_remaining | 5h | Tempo real |
| **daily_charge_kwh** 🆕 | **6.50 kWh** | **Acumula** |
| **daily_discharge_kwh** 🆕 | **2.00 kWh** | **Acumula** |

## 📦 Instalação

### Atualização Simples

```bash
1. Substituir 2 arquivos:
   - const.py
   - sensor.py

2. Reiniciar Home Assistant

3. Pronto! Sensores aparecem automaticamente
```

## 📱 Card Simples

```yaml
type: entities
title: Energia Hoje
entities:
  - entity: sensor.daily_charge_kwh
    name: ⚡ Carregado
  - entity: sensor.daily_discharge_kwh
    name: 🔋 Descarregado
```

## 🔔 Automação Exemplo

```yaml
automation:
  - alias: "Consumo Alto"
    trigger:
      - platform: numeric_state
        entity_id: sensor.daily_discharge_kwh
        above: 5
    action:
      - service: notify.mobile_app
        data:
          message: "Consumo alto: {{ states('sensor.daily_discharge_kwh') }} kWh!"
```

## 🔍 Atributos

```yaml
sensor.daily_charge_kwh:
  attributes:
    last_reset_date: "2024-12-19"  # Último reset
    last_update: "14:30:00"        # Última atualização
    last_power: 1200.5             # Potência atual
    is_active: true                # Está carregando?
```

## ✅ Compatibilidade

✅ **Energy Dashboard** - Total increasing  
✅ **Utility Meter** - Para semana/mês  
✅ **Histórico** - Gráficos automáticos  
✅ **Estatísticas** - Médias e comparações  

## 📊 Exemplo Real

**Manhã:**
```
08:00 - Começa carga solar
09:00 - 1000W × 1h = 1.00 kWh
10:00 - 1500W × 1h = 1.50 kWh
11:00 - 2000W × 1h = 2.00 kWh
Total carregado: 4.50 kWh ✅
```

**Tarde:**
```
14:00 - Começa descarga
15:00 - 500W × 1h = 0.50 kWh
16:00 - 600W × 1h = 0.60 kWh
Total descarregado: 1.10 kWh ✅
```

**Fim do dia:**
```
Carregado: 4.50 kWh
Descarregado: 1.10 kWh
Balanço: +3.40 kWh ✅
```

## 💡 Dicas

### Ver Eficiência
```
Eficiência = (Descarregado ÷ Carregado) × 100
Exemplo: (2.00 ÷ 6.50) × 100 = 30.7%
```

### Calcular Economia
```
Economia = Descarregado × Preço kWh
Exemplo: 2.00 × R$ 0.85 = R$ 1.70
```

## 📚 Documentação

- **NEW_SENSORS_DAILY_ENERGY_v1.6.0.md** - Guia completo
- **CHANGELOG.md** - Histórico de mudanças

---

**Versão:** 1.6.0  
**Arquivos alterados:** 2 (const.py, sensor.py)  
**Reconfiguração:** ❌ Não precisa  
**Energy Dashboard:** ✅ Compatível  
**Status:** ✅ Pronto!
