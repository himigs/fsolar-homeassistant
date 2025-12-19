# 🚀 Guia Rápido de Instalação

## Instalação em 5 Passos

### 1️⃣ Backup do Plugin Original
```bash
# No servidor do Home Assistant
cd /config/custom_components/
cp -r fsolar fsolar_backup
```

### 2️⃣ Extrair o Novo Plugin
```bash
# Extrair o arquivo fsolar_modified.zip
unzip fsolar_modified.zip
```

### 3️⃣ Substituir o Plugin Antigo
```bash
# Remover plugin antigo
rm -rf fsolar

# Renomear plugin modificado
mv fsolar_modified fsolar
```

### 4️⃣ Reiniciar o Home Assistant
- Vá em **Configurações** → **Sistema** → **Reiniciar**
- Ou use o comando: `ha core restart`

### 5️⃣ Verificar o Novo Sensor
Após o reinício, você verá um novo sensor para cada bateria:
- `sensor.battery_XXXXX_time_remaining`

## 📋 Checklist Pós-Instalação

- [ ] Backup realizado
- [ ] Plugin substituído
- [ ] Home Assistant reiniciado
- [ ] Novo sensor aparecendo na lista de entidades
- [ ] Sensor mostrando valores (se bateria estiver carregando/descarregando)
- [ ] Logs sem erros relacionados ao FSolar

## 🔍 Verificar Instalação

### Via Interface do Home Assistant

1. Vá em **Configurações** → **Dispositivos e Serviços**
2. Encontre a integração **FSolar**
3. Clique no dispositivo da bateria
4. Verifique se o sensor **"Time Remaining"** está listado

### Via Developer Tools

1. Vá em **Developer Tools** → **Estados**
2. Procure por `sensor.battery_` + `time_remaining`
3. Verifique se o sensor existe e tem um valor

### Via Logs

```bash
# Verificar logs
ha core logs | grep fsolar
```

Você deve ver linhas como:
```
INFO (MainThread) [custom_components.fsolar] Found X devices
INFO (MainThread) [custom_components.fsolar] Successfully updated data for X devices
```

## 🐛 Troubleshooting

### Sensor não aparece?

**Solução 1: Recarregar a integração**
1. Configurações → Dispositivos e Serviços
2. FSolar → **⋮** → Recarregar

**Solução 2: Limpar cache**
```bash
rm -rf /config/.storage/core.entity_registry
# ATENÇÃO: Isso vai resetar o registro de entidades!
```

**Solução 3: Reinstalar integração**
1. Remover integração FSolar
2. Reiniciar Home Assistant
3. Adicionar integração novamente

### Sensor mostra "Unknown"?

**Causas possíveis:**
- Bateria em standby (sem carga/descarga)
- API não retornando dados de potência
- Problema de comunicação com a bateria

**Verificar:**
```yaml
# Em Developer Tools → Template
{{ states.sensor.battery_XXXXX_time_remaining.attributes }}
```

### Erro nos logs?

**Verificar logs específicos:**
```bash
# Logs do FSolar
ha core logs | grep "custom_components.fsolar"

# Logs de erro
ha core logs | grep ERROR
```

## 📱 Adicionar ao Dashboard

### Método Rápido
1. Editar Dashboard
2. Adicionar Card → **Entity**
3. Selecionar `sensor.battery_XXXXX_time_remaining`
4. Salvar

### Método Avançado
Copie um exemplo do arquivo `EXAMPLES.md` e cole no editor YAML do card.

## 🎯 Próximos Passos

Depois de instalar e verificar:

1. **Leia o README.md** - Entenda como funciona o cálculo
2. **Veja EXAMPLES.md** - Implemente automações úteis
3. **Crie automações** - Configure notificações personalizadas
4. **Monitore** - Observe o comportamento por alguns dias

## 💡 Dicas Importantes

### Bateria em Standby
Se a bateria está em standby, o sensor mostrará `unavailable` ou `unknown`. Isso é **normal** - não há tempo de descarga/carga quando não há consumo.

### Valores Flutuantes
O tempo restante vai **variar** conforme o consumo muda. É uma estimativa baseada no momento atual.

### Primeira Leitura
Após instalar, pode levar até 5 minutos (intervalo de atualização) para os valores aparecerem.

### Múltiplas Baterias
Se você tem múltiplas baterias, um sensor será criado para cada uma:
- `sensor.battery_001_time_remaining`
- `sensor.battery_002_time_remaining`
- etc.

## 📞 Suporte

### Logs Úteis para Debugging

```bash
# Ver todos os sensores FSolar
ha core logs | grep "FSolarSensor"

# Ver erros de cálculo
ha core logs | grep "time_remaining"

# Ver comunicação com API
ha core logs | grep "FSolarAPI"
```

### Reportar Problemas

Se encontrar bugs:
1. Ative logs de debug (opcional)
2. Capture os logs relevantes
3. Descreva o problema
4. Inclua configuração (sem senhas)

### Reverter para Versão Original

Se precisar voltar:
```bash
cd /config/custom_components/
rm -rf fsolar
mv fsolar_backup fsolar
# Reiniciar Home Assistant
```

## ✅ Instalação Bem Sucedida

Você saberá que está tudo certo quando:
- ✅ Sensor `time_remaining` aparece
- ✅ Mostra valores em horas quando bateria está ativa
- ✅ Ícone muda baseado no estado (carregando/descarregando)
- ✅ Atributos extras estão disponíveis
- ✅ Sem erros nos logs

## 🎉 Aproveite!

Agora você tem um contador de tempo restante funcional para sua bateria FSolar!

Explore os exemplos em `EXAMPLES.md` para ideias de automações e dashboards.
