# Configuração e Variáveis de Ambiente

Configure as variáveis no arquivo `.env` (raiz do projeto) ou diretamente em `consulta_cnpj_cpf/settings.py`.

## Banco de Dados
```
POSTGRES_DB=seu_db
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## CNPJÁ PRO
```
CNPJA_API_KEY=coloque_sua_chave
CNPJA_BASE_URL=https://api.cnpja.com
```

## Estratégia de Cache da API
- `CNPJA_STRATEGY`: CACHE, CACHE_IF_FRESH (padrão), CACHE_IF_ERROR, ONLINE
- `CNPJA_MAX_AGE_DAYS`: dias que o cache é considerado fresco (padrão: 14)
- `CNPJA_MAX_STALE_DAYS`: dias adicionais que podem ser usados em caso de erro online (padrão: 30)

Exemplo:
```
CNPJA_STRATEGY=CACHE_IF_FRESH
CNPJA_MAX_AGE_DAYS=14
CNPJA_MAX_STALE_DAYS=30
```

## DRF e Throttling
- Limite global de 100/min para `anon` e `user` em `consulta_cnpj_cpf/settings.py`.

## Delay entre requisições
- `DELAY_SECONDS` em `consulta/services.py` (padrão: 1s). Não há controle via UI.