# Visão Geral

Este projeto é um sistema web em Django para consulta de CNPJs usando a API CNPJÁ PRO. Ele oferece processamento em lote (CSV/XLSX) com efeito “streaming”, controles de execução (pausar/retomar/cancelar), histórico e exportações. Além do CNPJ, o sistema mapeia e exibe o número do Processo associado, quando fornecido.

## Objetivos principais
- Consultar dados de empresas por CNPJ via CNPJÁ PRO
- Operar em lote com feedback incremental (streaming)
- Registrar histórico das execuções e permitir exportação
- Reduzir custos/latência via estratégia de cache configurável

## Funcionalidades
- Entrada manual ou upload (CSV/XLSX)
- Leitura resiliente de arquivos (detecta colunas e/ou varre células)
- Suporte ao campo Processo em todo o fluxo
- Delay fixo entre chamadas (padrão: 1s) para respeitar limites
- Retries automáticos em 429, timeout e erros de conexão
- Histórico com data dd/mm/yy (sem horário)
- Exportações CSV/XLSX com Processo e normalização de e-mail (“Sem e-mail”)
- DRF endpoint para JSON completo e throttling global 100/min

## Componentes-chave
- `clients/cnpja.py`: cliente da API CNPJÁ PRO com parâmetros de cache
- `consulta/services.py`: integração com API, parsing, exportação, regras de retry/cache
- `consulta/views.py`: views e endpoints streaming (jobs_*) e exportações
- `consulta/templates/consulta/home.html`: UI (Resultados e Histórico)

Consulte [setup.md](setup.md) para executar localmente e [api.md](api.md) para os endpoints.