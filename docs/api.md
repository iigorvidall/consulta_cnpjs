# API (REST e Streaming)

## REST (DRF)
GET `/cnpj/<cnpj>/`
- Valida CNPJ e retorna o JSON completo vindo do CNPJÁ PRO.
- Erros: 400 (validação/cliente), 500 (interno).

## Streaming (Polling via sessão)
### POST `/jobs/start/`
- multipart/form-data com `csv_file` (.csv/.xlsx), ou
- application/json `{ "cnpjs": "11...,22..." }`
- Resposta: `{ "total": <int> }`

### POST `/jobs/step/`
- Processa o próximo item respeitando `DELAY_SECONDS`.
- Respostas possíveis:
  - `{ status: 'paused'|'cancelled', processed, total, item: null }`
  - `{ status: 'done', processed, total, item: null }`
  - `{ status: 'running', processed, total, item }` onde `item` contém `{ cnpj, nome, email, processo? }`

### POST `/jobs/finalize/`
- Persiste os resultados do job em `ConsultaHistorico`.
- Resposta: `{ status: 'ok' }`.

### POST `/jobs/pause/` `jobs/resume/` `jobs/cancel/`
- Controlam o estado do job na sessão.
- Respostas: `{ status: 'paused'|'running'|'cancelled' }`.

Observações:
- A fila do job armazena pares `{cnpj, processo}` e apenas pares idênticos são deduplicados.
- E-mails ausentes são normalizados para “Sem e-mail”.
- Data do histórico nos exports é dd/mm/yy.