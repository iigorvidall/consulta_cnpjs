# Solução de Problemas

## Read timed out / ConnectionError
- A API pode estar lenta/instável. O sistema tenta novamente automaticamente (até o limite). Verifique `CNPJA_STRATEGY` para favorecer cache.

## 429 Too Many Requests
- Aguarde. O sistema faz backoff e tenta novamente. Ajuste o delay se necessário.

## CSV com encoding quebrado
- O parser tenta `utf-8-sig` e cai para `latin-1`. Abra o arquivo e re-salve em UTF-8 se o problema persistir.

## Cabeçalho ausente (CNPJ/Processo)
- O sistema tenta varredura regex. Verifique se há dados legíveis em alguma coluna.

## E-mail ausente
- Exibirá “Sem e-mail”. Confira se a empresa realmente tem e-mail exposto na API.