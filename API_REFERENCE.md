# Referência da API FelicitySolar

Esta documentação detalha os endpoints e estruturas de dados descobertos através do mapeamento do portal web da FelicitySolar.

## Informações Base
* **Base URL:** `https://shine-api.felicitysolar.com`
* **Headers Padrão:**
  ```http
  Content-Type: application/json
  Accept: application/json, text/plain, */*
  lang: pt_BR
  Authorization: Bearer_<seu_token_aqui>
  ```

---

## 1. Autenticação

### `POST /userlogin`
Realiza o login e obtém o token de acesso. A senha deve ser criptografada via RSA usando a chave pública estática do portal antes do envio.

**Payload:**
```json
{
  "userName": "email@exemplo.com",
  "password": "senha_criptografada_em_base64",
  "version": "1.0"
}
```

**Resposta:** Retorna o token de acesso na chave `data.token` ou diretamente na raiz `token`.

---

## 2. Listagem de Dispositivos

### `POST /device/list_device_all_type`
Retorna a lista completa de dispositivos vinculados à conta.

**Payload:**
```json
{
  "pageNum": 1,
  "pageSize": 100,
  "deviceSn": "",
  "status": "",
  "sampleFlag": "",
  "oscFlag": ""
}
```

---

## 3. Dados em Tempo Real (Snapshot)

### `POST /device/get_device_snapshot`
Retorna o estado completo da bateria e do inversor em um momento específico. Este é o principal endpoint usado pela integração.

**Payload:**
```json
{
  "deviceSn": "072602410025330079",
  "deviceType": "BP",
  "dateStr": "YYYY-MM-DD HH:MM:SS"
}
```

### Mapeamento das Chaves de Resposta (`data`)

#### Métricas Principais
* `battSoc` / `emsSoc`: Estado de Carga (%)
* `battSoh` / `emsSoh`: Saúde da Bateria (%)
* `battVolt` / `emsVoltage`: Tensão Global da Bateria (V)
* `battCurr` / `emsCurrent`: Corrente Total (A) - *Negativo na descarga, positivo na carga.*
* `bmsPower` / `emsPower`: Potência Total (W)
* `battCapacity` / `emsCapacity`: Capacidade Nominal (Ah)
* `tempMax` / `tempMin`: Temperatura máxima e mínima geral (°C)

#### BMS e Células
* `bmsVoltageList`: Array contendo a tensão de cada célula individual em milivolts (mV). Ex: `["3326", "3326", "3327", ...]`. Valores como `32767` indicam sensores inexistentes/vazios.
* `cellTempList`: Array contendo a temperatura dos sensores individuais das células em °C. Valores como `3276.7` indicam sensores vazios.
* `maxVoltage2bms` / `minVoltage2bms`: Tensão da célula mais alta e mais baixa em mV.
* `maxCellTempNum` / `minBattTempNum`: Índice/Número da célula mais quente e mais fria.
* `maxVoltageNum2bms` / `minVoltageNum2bms`: Índice/Número da célula com maior e menor tensão.

#### Limites Operacionais (Configurados pelo BMS)
* `BMSLCVolt`: Limite de Tensão de Carga (Charging Voltage Limit)
* `BMSLDVolt`: Limite de Tensão de Descarga (Discharge Voltage Limit)
* `BMSLCCurr`: Limite de Corrente de Carga (Current Charging Limit)
* `BMSLDCurr`: Limite de Corrente de Descarga (Discharge Current Limit)

#### Especificações do Dispositivo (Nameplate)
Estes campos contêm dados estáticos de placa, retornados junto com o snapshot:
* `volt`: **Tensão nominal exata** da bateria (ex: `"25.6"` para um banco 24V LiFePO₄). Usado pela integração para calcular kWh automaticamente — **não requer configuração manual**.
* `rateVolt`: Classe de voltagem nominal simplificada (ex: `"24"` para 24V).
* `voltageLevel`: Nível de voltagem como inteiro (`1`=12V, `2`=24V, `3`=48V).
* `curr`: Corrente nominal (Ah) da bateria (ex: `"100"`).
* `ratedEnergy`: Energia nominal (kWh) da bateria (ex: `"2.56"`).
* `capacity`: Capacidade em Ah (equivalente ao `curr`).
* `nameplateRatedPower`: Potência nominal como string (ex: `"2.5kW"`).

#### Outros
* `heatCurr`: Corrente do aquecedor interno (A)
* `bmsChargingState`: Estado atual de fluxo. `0` = Standby, `1` = Carregando, `2` = Descarregando.

---

## 4. Dicionário de Estados (Enums)

### `bmsState` (Status da Bateria)
O campo `bmsState` é um bitmask ou enumeração que dita o estado operacional e as permissões do BMS. Algumas flags conhecidas:
* `8`: Forçar Carga Completa (Full Charge)
* `16`: Carga Imediata 2 (Charge Immediately 2)
* `32`: Carga Imediata 1 (Charge Immediately 1)
* `64`: Permissão de Descarga Ativada (Discharge Enable)
* `128`: Permissão de Carga Ativada (Charge Enable)
* `256`: Descarga MOS Ativada (Discharge MOS)
* `512`: Carga MOS Ativada (Charge MOS)
* `1024`: Descarga Soft MOS
* `2048`: Carga Soft MOS
* `4096`: Descarregando (Discharging)
* `8192`: Carregando (Charging)

### `workMode` (Modo de Trabalho)
Modo geral de operação do sistema:
* `0`: Modo Ligado (Power On Mode)
* `1`: Modo Espera (Standby Mode)
* `2`: Modo Bateria (Battery Mode)
* `3`: Modo Apenas Descarga (Discharge-Only Mode)
* `4`: Modo Apenas Carga (Charge-Only Mode)
* `5`: Modo Baixo Consumo (Low Power Mode)
* `6`: Modo de Falha (Fault Mode)
* `7`: Modo Desligado (Shutdown Mode)
* `8`: Modo de Teste (Test Mode)
* `9`: Modo de Atualização (Upgrade Mode)

### `heatStatus` (Status de Aquecimento)
* `0`: Não está aquecendo (NotHeating)
* `1`: Trocando para aquecimento (SwitchingtoHeat)
* `2`: Aquecendo (Heating)
* `3`: Aquecendo e Carregando (HeatingandCharging)
* `4`: Trocando para não aquecer (SwitchingtoNoHeat)
