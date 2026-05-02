# Changelog - FSolar Integration

## Versão 2.2.0 - Smart Sensors & HACS Ready (Maio/2026)

### ✨ Novas Funcionalidades:
- **Binary Sensors:** 3 novos sensores binários: `battery_charging`, `battery_discharging` e `battery_low`. Limite do `battery_low` é dinâmico — usa a reserva de segurança configurada ou 20% como padrão.
- **Sensor `last_update`:** Sensor diagnóstico de timestamp mostrando quando foi a última comunicação bem-sucedida com a API.
- **`hacs.json`:** Integração agora é descobrível e instalável diretamente pelo HACS.
- **Ícone para Tema Claro:** Adicionado `brand/dark_icon.png` para exibição correta no tema claro do Home Assistant.

### 🔧 Melhorias:
- **`battery_remaining_kwh` com DOD:** Sensor de energia disponível agora subtrai a reserva de segurança do SOC, exibindo apenas a energia realmente utilizável.
- **`battery_capacity_kwh` via API:** Usa o campo `ratedEnergy` retornado diretamente pela API (valor exato de placa), com fallback para o cálculo Ah × V.

---

## Versão 2.1.0 - Zero Config, Smarter Sensors (Maio/2026)

### ✨ Melhorias:
- **Tensão Nominal Automática:** A tensão nominal da bateria agora é detectada automaticamente pela API (campos `volt` / `rateVolt`). O seletor manual de voltagem foi removido das configurações, simplificando a experiência do usuário.
- **Sensores de Tempo com `None`:** Os sensores `time_to_empty` e `time_to_full` agora retornam *Indisponível* (`None`) quando não estão ativos (ex: `time_to_empty` fica indisponível durante a carga). Isso elimina falsos disparos em automações, sem necessidade de condicionar o status de carga.
- **Limpeza de Código:** Removidos imports mortos em `__init__.py` e constantes nunca utilizadas (`CONF_EMAIL`, `DEVICE_STATUS`, `BATTERY_MODES`) em `const.py`.
- **Correção de Traduções:** Chave `email` corrigida para `username` nos arquivos `en.json` e `pt.json`, e entradas obsoletas de `nominal_voltage` removidas.

---

## Versão 2.0.0 - Refatoração Arquitetural Completa (Maio/2026)

Esta é a maior atualização desde o lançamento do plugin, reconstruindo toda a fundação do código para se alinhar aos rigorosos padrões oficiais do Home Assistant.

### 🛠️ Mudanças Core:
- **`SensorEntityDescription`:** Todos os mais de 20 sensores abandonaram dicionários pesados em favor das classes modernas do Home Assistant, reduzindo a complexidade ciclomática em quase 80%.
- **Isolamento de Classes:** O cálculo de energia acumulada agora mora na `FSolarDailyEnergySensor` (herdando `RestoreEntity` corretamente), prevenindo qualquer conflito de estados ou perda de dados durante reinícios.
- **Coordenador Desacoplado:** A classe `FSolarDataUpdateCoordinator` foi movida para seu próprio arquivo (`coordinator.py`), limpando o setup (`__init__.py`).
- **Performance:** Avaliações assíncronas simplificadas para extrair métricas BMS sem repetições pesadas.
- **Documentação Limpa:** Múltiplos tutoriais fragmentados (`INSTALL.md`, `GUIA_VISUAL.md`, etc) foram unidos no `README.md` principal, preparando o projeto para submissão ao HACS oficial.

---

## Versões Anteriores (1.1.0 - 1.6.1)

### 1.6.1 (Dez/2024) - Correções Críticas
- **Bug Fix:** O `time_remaining` retornava `0` quando a bateria estava em standby. *(Nota: na versão 2.1.0 este comportamento foi revisado — o sensor agora retorna `None`/Indisponível ao invés de `0`, prevenindo falsos disparos em automações.)*
- **Bug Fix:** Correção na falha que reiniciava os sensores diários ao religar o Home Assistant. O valor agora persiste com base na validação da data (`_last_reset_date`).

### 1.6.0 (Dez/2024) - Lançamento dos Sensores Diários
- Criados os sensores de energia `daily_charge_kwh` e `daily_discharge_kwh`.
- Suporte oficial ao Energy Dashboard do Home Assistant via state class `total_increasing`.
- Reset automático interno implementado (dispensa automações manuais).

### 1.5.0 (Dez/2024) - Sensor Remanescente
- Adicionado o sensor `battery_remaining_kwh` que mostra quanta energia (kWh) você tem disponível **AGORA** multiplicando a voltagem nominal pela porcentagem atual da bateria.

### 1.4.0 a 1.2.0 (Dez/2024) - Options Flow e Debugging 
- **Options Flow:** Suporte a mudar a voltagem da bateria via painel do Home Assistant (Options), sem editar yaml.
- Múltiplos tratamentos de potências ativas para evitar falhas de interpretação nas baterias antigas de 12V.

### 1.1.0 - Cálculo de Autonomia
- Implementação da lógica preditiva `time_remaining`. Ícones dinâmicos de carga/descarga dependendo do fluxo energético.
