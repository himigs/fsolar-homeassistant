# Changelog - FSolar Plugin Modificado

## Versão 1.6.0 - Sensores de Energia Diária (2024-12-19)

### 🆕 Dois Novos Sensores para Energy Dashboard

#### daily_charge_kwh e daily_discharge_kwh
**Acumulam energia localmente e resetam à meia-noite automaticamente!**

**Características:**
- ✅ **daily_charge_kwh**: Energia carregada hoje (kWh)
- ✅ **daily_discharge_kwh**: Energia descarregada hoje (kWh)
- ✅ Cálculo local: `Energia = Potência × Tempo`
- ✅ Acumula durante o dia
- ✅ Reset automático à meia-noite (00:00)
- ✅ Persiste entre reinícios
- ✅ **Compatível com Energy Dashboard do Home Assistant**

**Fórmula:**
```
A cada atualização:
Energia (kWh) = (Potência W × Tempo h) ÷ 1000
Acumula no total do dia
```

**Exemplo:**
```
Manhã:   1000W × 2h = 2.00 kWh
Tarde:   1500W × 3h = 4.50 kWh
Total carregado: 6.50 kWh

Noite:   500W × 4h = 2.00 kWh
Total descarregado: 2.00 kWh
```

### 📊 Integração com Energy Dashboard

**Como configurar:**
1. Configurações → Dashboards → Energia
2. Armazenamento de Bateria:
   - Entrada: `sensor.daily_charge_kwh`
   - Saída: `sensor.daily_discharge_kwh`
3. Salvar

**Resultado:**
- Veja energia carregada/descarregada por dia
- Gráficos históricos automáticos
- Comparação entre dias
- Balanço energético

### 📝 Atributos dos Sensores

```yaml
sensor.daily_charge_kwh:
  state: 6.50 kWh
  attributes:
    last_reset_date: "2024-12-19"   # Data do último reset
    last_update: "14:30:00"          # Última atualização
    last_power: 1200.5               # Potência atual (W)
    charging_status: "Charging"
    is_active: true
    
sensor.daily_discharge_kwh:
  state: 2.00 kWh
  attributes:
    last_reset_date: "2024-12-19"
    last_update: "14:30:00"
    last_power: 450.2
    charging_status: "Standby"
    is_active: false
```

### 📝 Mudanças Técnicas

**Arquivos Modificados:**
1. **const.py**
   - Adicionado `daily_charge_kwh`
   - Adicionado `daily_discharge_kwh`
   - State class: `total_increasing` (para Energy Dashboard)

2. **sensor.py**
   - Herdado `RestoreEntity` para persistência
   - Método `_calculate_daily_energy()` criado
   - Lógica de acumulação e reset automático
   - Restauração de estado ao reiniciar
   - Detecção de mudança de dia

### 🎯 Casos de Uso

**Perfeito para:**
- Energy Dashboard do Home Assistant
- Monitorar consumo diário
- Relatórios de energia
- Automações baseadas em consumo
- Cálculo de custos
- Comparação dia-a-dia

### 📚 Documentação

**Novo arquivo:** `NEW_SENSORS_DAILY_ENERGY_v1.6.0.md`
- Guia completo
- Integração com Energy Dashboard
- Exemplos de automações
- Cards e dashboards
- Troubleshooting

### ⚠️ Atualização

✅ Apenas 2 arquivos modificados:
- `const.py`
- `sensor.py`

✅ Sem reconfiguração necessária
✅ Sensores aparecem automaticamente
✅ Começam acumulando do zero

---

## Versão 1.5.0 - Novo Sensor battery_remaining_kwh (2024-12-19)

### 🆕 Novo Sensor: Energia Disponível

#### Sensor battery_remaining_kwh
**Mostra a energia disponível atual em kWh!**

**O que faz:**
- ✅ Calcula energia disponível: `Capacidade kWh × SOC%`
- ✅ Atualiza em tempo real com SOC
- ✅ Mostra quanto você tem AGORA para usar
- ✅ Perfeito para automações inteligentes

**Fórmula:**
```
Energia Disponível = (Capacidade Total kWh × SOC) ÷ 100

Exemplo:
2.56 kWh × 42% = 1.08 kWh disponíveis
```

### 📊 Três Sensores Agora

| Sensor | Valor | Descrição |
|--------|-------|-----------|
| battery_capacity | 100 Ah | Capacidade em Ah |
| battery_capacity_kwh | 2.56 kWh | Capacidade total |
| battery_remaining_kwh 🆕 | 1.08 kWh | Energia disponível AGORA |

### 🎯 Casos de Uso

**Perfeito para:**
- Saber energia disponível em tempo real
- Automações de economia de energia
- Ligar gerador quando bateria baixa
- Calcular autonomia restante
- Integração com Energy Dashboard

### 📝 Atributos do Sensor

```yaml
sensor.battery_remaining_kwh:
  state: 1.08 kWh
  attributes:
    capacity_ah: 100              # Capacidade original
    total_capacity_kwh: 2.56      # Capacidade total
    current_soc: 42               # SOC atual
    nominal_voltage_v: 25.6       # Tensão configurada
    current_voltage_v: 25.6       # Voltagem atual
    charging_status: Charging     # Status
```

### 📝 Mudanças Técnicas

**Arquivos Modificados:**
1. **const.py**
   - Adicionado sensor `battery_remaining_kwh`
   - Device class: energy
   - State class: measurement

2. **sensor.py**
   - Nova lógica de cálculo
   - Multiplica capacidade_kwh por SOC%
   - Atributos detalhados

### 📚 Documentação

**Novo arquivo:** `NEW_SENSOR_REMAINING_v1.5.0.md`
- Guia completo
- Exemplos de automações
- Cards e dashboards
- Casos de uso práticos

### ⚠️ Atualização Simples

✅ Apenas substitua 2 arquivos:
- `const.py`
- `sensor.py`

✅ Reinicie e pronto!  
✅ Novo sensor aparece automaticamente  
✅ Não quebra nada existente  

---

## Versão 1.4.0 - Novo Sensor battery_capacity_kwh (2024-12-19)

### 🆕 Novo Sensor

#### Sensor battery_capacity_kwh
**Capacidade da bateria em kWh**, calculada automaticamente!

**Características:**
- ✅ Calcula Ah → kWh usando tensão nominal
- ✅ **Configurável DEPOIS da instalação** via interface
- ✅ Dropdown com opções: 12.8V, 25.6V, 51.2V
- ✅ Padrão: 25.6V (bateria 24V)
- ✅ Atributos detalhados (Ah, tensão nominal, tensão atual)

**Fórmula:**
```
Capacidade (kWh) = (Capacidade Ah × Tensão Nominal V) ÷ 1000
```

**Exemplo:**
- 100 Ah × 25.6V = **2.56 kWh** ✅

### ⚙️ Configuração Via Interface

**NÃO precisa configurar durante instalação!**

Depois de instalar:
1. **Configurações** → **Dispositivos e Serviços**
2. **FSolar** → **CONFIGURAR** (⚙️)
3. Selecionar tensão: 12.8V / 25.6V / 51.2V
4. Reiniciar Home Assistant

**Opções:**
- 12V LiFePO₄ (12.8V)
- 24V LiFePO₄ (25.6V) - Padrão
- 48V LiFePO₄ (51.2V)

### 📝 Mudanças Técnicas

**Arquivos Modificados:**
1. **const.py**
   - Adicionado sensor `battery_capacity_kwh`
   - Unidade: kWh
   - Device class: energy_storage

2. **config_flow.py**
   - Adicionado `OptionsFlowHandler`
   - Campo configurável: `nominal_voltage`
   - Dropdown com 3 opções
   - Acessível via botão CONFIGURAR

3. **sensor.py**
   - Nova lógica de cálculo para `battery_capacity_kwh`
   - Lê tensão de `entry.options`
   - Atualiza automaticamente ao mudar configuração
   - Atributos: capacity_ah, nominal_voltage_v, current_voltage_v

### 📊 Comparação de Sensores

| Sensor | Valor | Unidade | Fonte |
|--------|-------|---------|-------|
| battery_capacity | 100 | Ah | API FSolar |
| battery_capacity_kwh 🆕 | 2.56 | kWh | Calculado |

### 🎯 Casos de Uso

**battery_capacity (Ah):**
- Especificações técnicas
- Comparação com manual
- Cálculos por corrente

**battery_capacity_kwh (kWh):**
- Energia total armazenada
- Comparação com consumo
- Dashboards de energia

### 📚 Documentação

**Novos arquivos:**
- `CONFIGURAR_TENSAO.md` - Guia passo-a-passo de configuração
- `NEW_SENSOR_KWH_v1.4.0.md` - Documentação completa
- `QUICK_START_v1.4.0.md` - Guia rápido

### ⚠️ Compatibilidade

✅ Totalmente compatível com versão anterior
✅ Sensor antigo (Ah) continua funcionando
✅ Não quebra automações existentes
✅ Tensão padrão: 25.6V (bateria 24V)
✅ Configurável via interface

---

## Versão 1.3.0 - Correção Final battery_capacity (2024-12-19)

### 🎯 Solução Simplificada

**Problema:** Sensor `battery_capacity` mostrava valores em unidade incorreta.
- API retorna: **100 Ah**
- Sensor mostrava: **100 kWh** ❌

**Solução:** Manter o valor original da API em **Ah** sem conversão!

### 📝 Mudanças Implementadas

1. **Unidade Corrigida**
   - Antes: `kWh` ❌
   - Depois: `Ah` ✅
   - Alterado em: `const.py`

2. **Sem Conversão**
   - Removida toda lógica de conversão Ah → kWh
   - Sensor mostra valor direto da API: **100 Ah**
   - Simplificado em: `sensor.py`

3. **Atributos Simplificados**
   ```yaml
   voltage_v: 25.6          # Voltagem para referência
   ems_capacity_ah: 100     # Se disponível
   rated_energy_wh: 2560    # Se disponível
   ```

### ✅ Resultado

```yaml
# Antes (v1.2.1):
sensor.battery_capacity: 100 kWh  ❌

# Depois (v1.3.0):
sensor.battery_capacity: 100 Ah   ✅
```

### 📊 Comparação de Versões

| Versão | Abordagem | Resultado |
|--------|-----------|-----------|
| 1.2.0 | Mostrava 100 kWh (errado) | ❌ |
| 1.2.1 | Convertia para 2.56 kWh | ⚠️ Complexo |
| 1.3.0 | Mostra 100 Ah (correto) | ✅ Simples |

### ⚠️ Impacto

- Se você usa `battery_capacity` em automações, revise os valores
- Agora os valores estão em **Ah** (não kWh)
- Template sensors podem ser necessários se você precisa de kWh

**Documentação:** `FINAL_FIX_v1.3.0.md`

---

## Versão 1.2.1 - Correção battery_capacity (2024-12-19)

**OBSOLETA** - Substituída pela v1.3.0 (abordagem mais simples)

---

## Versão 1.2.0 - Debug e Campos Adicionais (2024-12-19)

### 🐛 Correção Crítica

#### Sensor battery_capacity Mostrando Valores Errados
**Problema:** O sensor `battery_capacity` também estava mostrando valores incorretos, interpretando Ah como kWh diretamente.

**Exemplo do Problema:**
- API retorna: `100` (em Ampere-hora)
- Sensor mostrava: `100 kWh` ❌
- Valor correto: `2.56 kWh` (100 Ah × 25.6V ÷ 1000) ✅

#### Solução Implementada

1. **Conversão Automática no Sensor**
   - ✅ Detecta automaticamente se valor é Ah ou kWh
   - ✅ Converte Ah → kWh usando voltagem real da bateria
   - ✅ Mostra valor correto em kWh no estado principal
   - ✅ Usa mesma heurística do time_remaining (> 50 = Ah)

2. **Novos Atributos Adicionados**
   ```yaml
   capacity_ah: 100          # Valor original em Ah
   capacity_kwh: 2.56        # Valor convertido em kWh
   voltage_v: 25.6           # Voltagem usada na conversão
   ems_capacity: 100         # Se disponível
   rated_energy: 2560        # Se disponível
   voltage_assumed: true     # Se voltagem foi estimada
   ```

3. **Logs Informativos**
   - INFO quando faz conversão: "Converting battery_capacity: 100.0 Ah × 25.6 V = 2.56 kWh"
   - WARNING quando usa voltagem estimada

#### Comparação

| Métrica | Antes (v1.2.0) | Depois (v1.2.1) |
|---------|----------------|-----------------|
| Estado principal | 100 kWh ❌ | 2.56 kWh ✅ |
| Atributo capacity_ah | ❌ Não existe | ✅ 100 |
| Atributo capacity_kwh | ❌ Não existe | ✅ 2.56 |
| Atributo voltage_v | ❌ Não existe | ✅ 25.6 |

#### Impacto

⚠️ **ATENÇÃO:** Se você tem automações ou templates usando `sensor.battery_capacity`, os valores agora estarão corretos mas muito menores que antes. Revise suas automações!

**Documentação:** Veja `UPDATE_BATTERY_CAPACITY.md` para guia completo de migração.

---

## Versão 1.2.0 - Debug e Campos Adicionais (2024-12-19)

### 🔧 Correções e Melhorias

#### Problema Identificado
Alguns sistemas FSolar não retornam dados de potência nos campos padrão (`batCharPower`, `bmsPowerCharging`, etc), causando o sensor `time_remaining` a mostrar "desconhecido" mesmo durante carga/descarga ativa.

#### Soluções Implementadas

1. **Campos Adicionais de Potência**
   - ✅ Adicionado `batChargePower` para carga
   - ✅ Adicionado `chargerPower` para carga
   - ✅ Adicionado `batDischargePower` para descarga
   - ✅ Adicionado `dischargingPower` para descarga
   - ✅ Melhorado uso de `bmsPower` e `emsPower` como fallback

2. **Logs de Debug Detalhados**
   - ✅ Log de todos os campos disponíveis na API
   - ✅ Log dos valores de SOC, capacidade e estado
   - ✅ Log dos valores de potência encontrados
   - ✅ Log de fallback tentados
   - ✅ Warning detalhado quando campo não encontrado
   - ✅ Info quando cálculo é bem sucedido

3. **Atributos de Debug**
   - ✅ Adicionado `debug_no_power` nos atributos quando potência não encontrada
   - ✅ Melhoria nos atributos extras com múltiplas tentativas

#### Exemplo de Logs

**Quando funciona:**
```
INFO [custom_components.fsolar.sensor] Device 074502410025370192 charging: SOC=41%, Capacity=100 kWh, Power=5000 W, Time=11.8 h
```

**Quando falta potência:**
```
WARNING [custom_components.fsolar.sensor] Device 074502410025370192 is charging but no power data available. Checked fields: ['batCharPower', 'bmsPowerCharging', 'chargingPower', 'batChargePower', 'chargerPower', 'bmsPower', 'emsPower']. All data keys: [...]
```

### 📝 Arquivos Modificados

#### `sensor.py`
- Função `_calculate_time_remaining()` expandida com:
  - 4 novos campos de tentativa para potência
  - Logs de debug em cada etapa
  - Melhor tratamento de fallback
- Função `extra_state_attributes` atualizada com:
  - Mesma lógica expandida de campos
  - Atributo `debug_no_power` quando aplicável

### 🐛 Troubleshooting

Para diagnosticar problemas, consulte o arquivo `TROUBLESHOOTING.md` que inclui:
- Como visualizar os logs
- O que procurar nos logs
- Comandos úteis
- Solução temporária com template sensor
- Checklist de verificação

### 📦 Nova Documentação

- `TROUBLESHOOTING.md` - Guia completo de diagnóstico

---

## Versão 1.1.0 - Tempo Restante (2024-12-19)

### ✨ Novas Funcionalidades

#### Sensor de Tempo Restante (`time_remaining`)
- ✅ Cálculo automático do tempo restante durante descarga
- ✅ Cálculo do tempo até carga completa durante carregamento
- ✅ Retorna `None` quando em standby
- ✅ Unidade: horas (h)
- ✅ Precisão: 2 casas decimais

#### Ícones Dinâmicos
- 🔋⚡ `mdi:battery-charging` - Durante carregamento
- 🔋⬇️ `mdi:battery-arrow-down` - Durante descarga
- 🔋🕐 `mdi:battery-clock` - Em standby

#### Atributos Extras do Sensor
Novos atributos disponíveis no sensor `time_remaining`:
- `charging_status` - Status textual (Standby/Charging/Discharging)
- `is_charging` - Boolean indicando se está carregando
- `is_discharging` - Boolean indicando se está descarregando
- `is_standby` - Boolean indicando se está em standby
- `current_soc` - SOC atual em porcentagem
- `battery_capacity_kwh` - Capacidade da bateria em kWh
- `current_power_w` - Potência atual em Watts
- `energy_available_kwh` - Energia disponível durante descarga
- `energy_needed_kwh` - Energia necessária para carga completa

### 📝 Arquivos Modificados

#### `const.py`
```diff
+ from homeassistant.const import UnitOfTime
+ ATTR_TIME_REMAINING = "time_remaining"

+ "time_remaining": {
+     "name": "Time Remaining",
+     "unit": UnitOfTime.HOURS,
+     "icon": "mdi:timer-outline",
+     "device_class": "duration",
+     "state_class": "measurement",
+ },
```

#### `sensor.py`
```diff
+ def _calculate_time_remaining(self, data: dict) -> float | None:
+     """Calculate time remaining based on current state."""
+     # Lógica de cálculo implementada
+     ...

+ @property
+ def icon(self) -> str | None:
+     """Return the icon to use based on state."""
+     # Ícone dinâmico baseado no estado
+     ...

# No método native_value:
+ if self._sensor_type == "time_remaining":
+     return self._calculate_time_remaining(data)

# No método extra_state_attributes:
+ if self._sensor_type == "time_remaining":
+     # Adicionar atributos detalhados do cálculo
+     ...
```

### 🧮 Fórmulas Implementadas

#### Tempo Restante (Descarga)
```
Tempo (h) = (SOC% × Capacidade_kWh × 1000) ÷ Potência_Descarga_W
```

Onde:
- `SOC%` = Estado de carga atual (0-100)
- `Capacidade_kWh` = Capacidade nominal da bateria
- `Potência_Descarga_W` = Potência de descarga atual em Watts
- Resultado em horas com 2 decimais

#### Tempo até Carga Completa
```
Tempo (h) = ((100 - SOC%) × Capacidade_kWh × 1000) ÷ Potência_Carga_W
```

Onde:
- `(100 - SOC%)` = Carga restante para 100%
- `Capacidade_kWh` = Capacidade nominal da bateria
- `Potência_Carga_W` = Potência de carga atual em Watts
- Resultado em horas com 2 decimais

### 🔍 Dados da API Utilizados

O sensor utiliza os seguintes campos da API FSolar:

**State of Charge (SOC):**
- `battSoc` (prioritário)
- `emsSoc` (fallback)

**Capacidade:**
- `battCapacity` (prioritário)
- `emsCapacity` (fallback)
- `totalEmsCapacity` (último fallback)

**Status de Carga:**
- `bmsChargingState`
  - `0` = Standby
  - `1` = Charging
  - `2` = Discharging

**Potência de Descarga:**
- `batDisPower` (prioritário)
- `bmsPowerDischarge` (fallback)

**Potência de Carga:**
- `batCharPower` (prioritário)
- `bmsPowerCharging` (fallback)
- `chargingPower` (último fallback)

### ⚠️ Limitações Conhecidas

1. **Consumo Variável**: O cálculo assume consumo/carga constante. Mudanças no consumo afetarão a precisão.

2. **Eficiência**: Não considera perdas por eficiência da bateria (geralmente 90-95%).

3. **Standby**: Retorna `None` quando a bateria está em standby (sem carga/descarga ativa).

4. **Dados Insuficientes**: Retorna `None` se:
   - SOC não disponível
   - Capacidade não disponível
   - Potência de carga/descarga não disponível ou zero

5. **Precisão**: É uma **estimativa** baseada no estado atual, não uma previsão com machine learning.

### 🐛 Correções

- ✅ Tratamento de valores `None` nos cálculos
- ✅ Validação de divisão por zero
- ✅ Conversão segura de tipos (str → float)
- ✅ Logging de erros sem quebrar o sensor

### 📚 Documentação Adicional

Novos arquivos de documentação incluídos:
- `README.md` - Documentação principal em português
- `EXAMPLES.md` - Exemplos práticos de uso no Home Assistant
- `CHANGELOG.md` - Este arquivo

### 🔄 Compatibilidade

- ✅ Compatível com Home Assistant 2023.x+
- ✅ Mantém retrocompatibilidade com todos os sensores existentes
- ✅ Não requer mudanças em configurações existentes
- ✅ Adiciona sensor automaticamente ao reiniciar

### 📦 Instalação

1. Backup do plugin original
2. Substituir pasta `fsolar` por `fsolar_modified`
3. Renomear para `fsolar`
4. Reiniciar Home Assistant
5. Novo sensor aparece automaticamente

### 🎯 Próximas Melhorias (Roadmap)

Possíveis adições futuras:
- [x] Mais campos de potência (v1.2.0)
- [x] Logs detalhados para debug (v1.2.0)
- [ ] Previsão com histórico (machine learning)
- [ ] Consideração de eficiência configurável
- [ ] Média móvel para suavizar variações
- [ ] Alertas configuráveis integrados
- [ ] Gráficos de tendência
- [ ] API para consulta externa

### 👥 Contribuições

Este plugin modificado foi criado para adicionar funcionalidade de tempo restante.
Sugestões e melhorias são bem-vindas!

### 📄 Licença

Mantém a mesma licença do plugin original FSolar.

---

**Nota**: Esta é uma modificação não oficial do plugin FSolar.
Para suporte oficial, consulte o repositório original do FSolar.
