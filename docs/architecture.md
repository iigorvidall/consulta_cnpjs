# Arquitetura e Componentes

## Componentes
- `clients/cnpja.py`: Cliente HTTP para CNPJÁ PRO. Monta cabeçalhos, valida CNPJ, envia parâmetros de cache.
- `consulta/services.py`: Regras de negócio: consulta à API (timeout=30s, retries 429/timeout/conexão), parsing CSV/XLSX, exportações, delay entre chamadas.
- `consulta/views.py`: Views da UI e endpoints de streaming (`jobs_*`), histórico e exportações.
- `consulta/templates/consulta/home.html`: Interface com formulários, botões de controle e tabelas.
- `consulta/models.py`: Modelo `ConsultaHistorico` (armazenamento do resultado do job).

## Fluxo de Dados (Streaming)
1. UI chama `POST /jobs/start/` com CSV/XLSX (campo `csv_file`) ou JSON `{cnpjs: "11...,22..."}`.
2. Servidor valida/extrai itens e guarda na sessão: `job.queue = [{cnpj, processo}, ...]`.
3. UI chama `POST /jobs/step/` em loop; servidor aguarda `DELAY_SECONDS`, consulta API e retorna item.
4. Resultado incremental é exibido na tabela de Resultados.
5. Ao fim, UI chama `POST /jobs/finalize/` para persistir o histórico.

## Estado do Job (Sessão)
```
job = {
  queue: [{cnpj: str, processo: str|None}, ...],
  processed: int,
  total: int,
  results: [ {cnpj, nome, email, processo?}, ... ],
  status: 'running'|'paused'|'cancelled',
  tipo: 'upload'|'manual',
  arquivo_nome: str|None,
  cnpjs_str: '11...,22...'
}
```

## Estratégia de Cache
Os parâmetros (strategy, maxAge, maxStale) são passados ao CNPJÁ PRO e podem reduzir custos/latência retornando dados de cache quando apropriado.