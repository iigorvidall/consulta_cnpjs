# Operação e Resiliência

## Delay
- `DELAY_SECONDS` (services.py) define a espera entre passos/consultas.

## Retries
- `consultar_cnpj_api` faz retry em:
  - 429 (rate limit): aguarda e tenta novamente
  - Timeout/ConnectionError: aguarda e tenta novamente

## Throttling
- DRF com limite global de 100/min para anon/user.

## Estratégia de Cache
- Enviada ao CNPJÁ PRO (strategy/maxAge/maxStale) para reduzir custos e latência sempre que possível.