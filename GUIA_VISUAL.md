# 🖼️ Guia Visual - Configurar Tensão Nominal

## 📸 Como Fica a Interface

### 1️⃣ Localizar a Integração

Vá em **Configurações** → **Dispositivos e Serviços**

```
┌────────────────────────────────────────────────┐
│  Dispositivos e Serviços                       │
├────────────────────────────────────────────────┤
│                                                │
│  🔌 Integrações Configuradas                   │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │  🔋 FSolar                               │ │
│  │  user@email.com                          │ │
│  │                                          │ │
│  │  📊 10 entidades  🔋 1 dispositivo       │ │
│  │                                          │ │
│  │  [CONFIGURAR ⚙️]  [EXCLUIR]             │ │
│  └──────────────────────────────────────────┘ │
│                                                │
└────────────────────────────────────────────────┘
```

👆 Clique em **CONFIGURAR ⚙️**

### 2️⃣ Tela de Configuração

```
┌────────────────────────────────────────────────┐
│  ← Configurar FSolar                           │
├────────────────────────────────────────────────┤
│                                                │
│  Selecione a tensão nominal da sua bateria.   │
│  Isso será usado para calcular a capacidade   │
│  em kWh.                                       │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │  Tensão Nominal *                        │ │
│  │                                          │ │
│  │  ┌────────────────────────────────────┐ │ │
│  │  │ ▼ 24V LiFePO₄ (25.6V)             │ │ │
│  │  └────────────────────────────────────┘ │ │
│  │                                          │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│           [ENVIAR]    [CANCELAR]               │
│                                                │
└────────────────────────────────────────────────┘
```

### 3️⃣ Opções do Dropdown

Clique no dropdown para ver as opções:

```
┌────────────────────────────────────────────────┐
│  Tensão Nominal *                              │
│                                                │
│  ┌────────────────────────────────────────────┐│
│  │ 12V LiFePO₄ (12.8V)                       ││
│  ├────────────────────────────────────────────┤│
│  │ 24V LiFePO₄ (25.6V)         ← Selecionado ││
│  ├────────────────────────────────────────────┤│
│  │ 48V LiFePO₄ (51.2V)                       ││
│  └────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
```

**3 opções claras e simples!**

### 4️⃣ Após Enviar

```
┌────────────────────────────────────────────────┐
│  ✅ Configuração salva com sucesso!            │
│                                                │
│  Reinicie o Home Assistant para aplicar as    │
│  mudanças.                                     │
│                                                │
│           [REINICIAR AGORA]                    │
│                                                │
└────────────────────────────────────────────────┘
```

### 5️⃣ Verificar Resultado

Após reiniciar, veja em **Developer Tools** → **Estados**:

```yaml
sensor.battery_capacity_kwh:
  state: 2.56                    ✅ Calculado!
  unit_of_measurement: kWh
  attributes:
    capacity_ah: 100
    nominal_voltage_v: 25.6      ✅ Sua configuração!
    current_voltage_v: 25.6
    device_class: energy_storage
    friendly_name: 074502410025370192 Battery Capacity kWh
```

## 🎯 Fluxo Completo

```
┌─────────────────┐
│   1. INSTALAR   │
│   Integração    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. USAR PADRÃO  │
│   (25.6V)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. CONFIGURAR   │
│   Tensão Certa  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. REINICIAR   │
│   Home Asst.    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   5. PRONTO!    │
│ Sensor correto  │
└─────────────────┘
```

## 📋 Tabela de Escolha

Use esta tabela para saber qual opção escolher:

| Se sua bateria é... | Escolha... | Resultado (100 Ah) |
|---------------------|------------|-------------------|
| **12V** (4 células) | 12V LiFePO₄ (12.8V) | 1.28 kWh |
| **24V** (8 células) | 24V LiFePO₄ (25.6V) | 2.56 kWh |
| **48V** (16 células) | 48V LiFePO₄ (51.2V) | 5.12 kWh |

## 🔍 Como Saber Qual Escolher?

### Método 1: Etiqueta da Bateria
Procure por:
- "12V" → Escolha 12.8V
- "24V" → Escolha 25.6V
- "48V" → Escolha 51.2V

### Método 2: Número de Células
Conte as células em série:
- **4S** = 4 células → 12.8V
- **8S** = 8 células → 25.6V
- **16S** = 16 células → 51.2V

### Método 3: Voltagem Atual
Veja o sensor `battery_voltage`:
- **12-14V** → Bateria 12V (escolha 12.8V)
- **24-29V** → Bateria 24V (escolha 25.6V)
- **48-58V** → Bateria 48V (escolha 51.2V)

## 💡 Dica Importante

**Não sabe?** Deixe no padrão 25.6V!

A maioria das baterias residenciais é 24V. Se estiver errado, você sempre pode mudar depois! 😉

## 🎨 Exemplo Real

**Seu caso:**
- Bateria: 100 Ah
- Tensão: 25.6V (24V)
- Resultado: **2.56 kWh**

**Na interface:**
```
1. FSolar → CONFIGURAR ⚙️
2. Tensão Nominal: [24V LiFePO₄ (25.6V)] ✅
3. ENVIAR
4. Reiniciar
```

**Sensores resultantes:**
```yaml
sensor.battery_capacity: 100 Ah           ✅
sensor.battery_capacity_kwh: 2.56 kWh    ✅
```

## ✅ Checklist Visual

- [ ] Abri Configurações → Dispositivos e Serviços
- [ ] Encontrei a integração FSolar
- [ ] Cliquei em CONFIGURAR ⚙️
- [ ] Selecionei tensão correta no dropdown
- [ ] Cliquei em ENVIAR
- [ ] Reiniciei o Home Assistant
- [ ] Verifiquei sensor battery_capacity_kwh
- [ ] Valor está correto! 🎉

## 🎉 Pronto!

Agora você tem configuração visual e intuitiva da tensão nominal, direto na interface do Home Assistant!

Sem editar arquivos, sem código, sem complicação! 👍

---

**Versão:** 1.4.0  
**Interface:** ✅ Amigável  
**Configuração:** ✅ Visual  
**Resultado:** ✅ Perfeito
