# FSolar Home Assistant Integration

Integração customizada para Home Assistant para monitorar sistemas de bateria FelicitySolar (Shine API).

## 🌟 Funcionalidades

- **Login Nativo:** Não é mais necessário encriptar sua senha manualmente. Apenas digite seu email e senha de forma segura!
- **Monitoramento em Tempo Real:** Acompanhe SOC (%), Voltagem, Corrente, Potência e Temperatura.
- **Painel de Energia (Energy Dashboard):** Rastreamento de carga e descarga diária em kWh, com proteção nativa contra picos falsos após reinícios do sistema.
- **Tempo Restante Dinâmico:** Calcula automaticamente o tempo estimado para a bateria carregar completamente ou descarregar.
- **Dispositivos Agrupados:** Todos os sensores são organizados sob um único dispositivo na interface do Home Assistant, seguindo os padrões oficiais.

## 📦 Instalação

### HACS (Recomendado)
1. Abra o HACS no seu Home Assistant.
2. Vá em **Integrações** > **Repositórios Customizados** (Três pontos no canto superior direito).
3. Adicione a URL deste repositório e selecione a categoria `Integration`.
4. Instale "FSolar Battery" e reinicie o Home Assistant.

### Instalação Manual
1. Faça o download da última versão deste repositório.
2. Copie a pasta `fsolar-homeassistant` (renomeie para `fsolar` se preferir) para o diretório `custom_components` do seu Home Assistant.
3. Reinicie o Home Assistant.

## ⚙️ Configuração

1. No Home Assistant, vá em **Configurações** > **Dispositivos e Serviços**.
2. Clique em **Adicionar Integração** e busque por **FSolar Battery**.
3. Insira suas credenciais do portal FelicitySolar (Email e Senha).
   - *Nota: Deixe "Password Already Encrypted" desmarcado, a menos que esteja usando uma string RSA pré-gerada muito antiga.*
4. Clique em Enviar.

### 📊 Integração com Painel de Energia (Energy Dashboard)

Para visualizar o balanço diário da bateria no Painel de Energia nativo do Home Assistant:
1. Vá em **Configurações** > **Dashboards** > **Energia**.
2. Na seção **Armazenamento de Bateria**, adicione as entidades correspondentes:
   - **Energia que entra na bateria (Carga):** `sensor.[id_da_bateria]_daily_charge_kwh`
   - **Energia que sai da bateria (Descarga):** `sensor.[id_da_bateria]_daily_discharge_kwh`
3. Salve. O painel começará a exibir gráficos nas próximas 2 horas. *(Nota: estes sensores são resetados automaticamente todo dia à meia-noite).*

## 📊 Principais Sensores Disponíveis

| Nome do Sensor | Descrição |
|-------------|-------------|
| `Battery SOC` | Estado de carga atual (%) |
| `Battery Voltage` | Voltagem atual (V) |
| `Battery Current` | Corrente fluindo (A) |
| `Battery Power` | Potência instantânea (W) |
| `Battery Temperature` | Temperatura interna (°C) |
| `Time to Empty` | Tempo estimado até descarregar completamente (h). Fica *Indisponível* enquanto carregando. |
| `Time to Full` | Tempo estimado até carga completa (h). Fica *Indisponível* enquanto descarregando. |
| `Daily Charge` | Total de energia carregada hoje (kWh) |
| `Daily Discharge` | Total de energia descarregada hoje (kWh) |
| `Battery Health` | Saúde estimada da bateria (%) |
| `Cycles` | Ciclos totais de carga/descarga |
| `Battery Remaining kWh` | Energia disponível no momento (kWh) — calculada com tensão nominal detectada automaticamente pela API |
| `Cell Voltages` | Mapeamento individual de voltagem das células (Diagnóstico) |

## 🛠️ Dicas e Soluções

- **Credenciais Inválidas:** Verifique se o email e a senha são idênticos aos usados no app FelicitySolar (Shine).
- **Sensores Indisponíveis (Unavailable):** Pode ocorrer se a API falhar no primeiro boot, mas o sistema tentará reconectar automaticamente.
- **Painéis customizados:** Veja o arquivo `EXAMPLES.md` na raiz do projeto para criar dashboards incríveis com os dados gerados.

## ✨ Créditos

Desenvolvido para expandir as capacidades de monitoramento em tempo real de baterias FelicitySolar, empregando Injeção de Dependências, `SensorEntityDescriptions` e arquiteturas modernas exigidas pelo ecossistema Home Assistant.
