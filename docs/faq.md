# FAQ

## O que é o campo Processo?
Número/identificador associado ao CNPJ na sua planilha/controle. Ele é lido do CSV/XLSX (se houver coluna) e exibido junto ao resultado.

## Posso repetir o mesmo CNPJ com processos diferentes?
Sim. O sistema deduplica apenas pares idênticos (mesmo CNPJ e mesmo Processo).

## Como funciona o cache do CNPJÁ?
A estratégia (strategy) e os limites (maxAge/maxStale) são enviados como query params. Isso pode evitar consultas online e poupar créditos.

## Posso mudar o delay entre as consultas?
Sim, altere `DELAY_SECONDS` em `consulta/services.py`. Não há controle na interface.