# Importação de Arquivos (CSV/XLSX)

## CSV
- Preferência por cabeçalhos: `cnpj`, `CNPJ`, `CNPJ/CPF`, `cnpj_cpf` (CNPJ) e `processo`, `número do processo`, `numero do processo` (Processo)
- Se cabeçalhos não forem adequados, o sistema vasculha cada linha buscando padrões de CNPJ com regex
- Encodings suportados: tenta `utf-8-sig`, cai para `latin-1` quando necessário

## XLSX
- Detecta colunas de cabeçalho na primeira linha para CNPJ/Processo
- Se não encontrar, faz varredura por células com regex de CNPJ

## Observações
- A fila do job guarda pares `{cnpj, processo}`; CNPJs repetidos com processos diferentes serão processados
- Apenas pares idênticos são deduplicados