# Importação de Arquivos (CSV/XLSX)

## CSV
 Preferência por cabeçalhos (CNPJ): `cnpj`, `CNPJ`, `CNPJ/CPF`, `cnpj_cpf`, `NRCPFCNPJ`, `CNPJCPF`, `cpf/cnpj`.
 Preferência por cabeçalhos (Processo): `processo`, `Processo`, `número do processo`, `numero do processo`, `DSProcesso`, `dsprocesso`.
 Se cabeçalhos não forem adequados, o sistema vasculha cada linha e extrai por padrões:
  - CNPJ: 14 dígitos puros ou máscara `00.000.000/0000-00`.
  - Processo: `xxx.xxx/xxxx` (ex.: `870.800/2017`) ou 10 dígitos puros.
  - Quando detectado como 10 dígitos, o Processo é normalizado para `xxx.xxx/xxxx`.

## XLSX
 Detecta colunas de cabeçalho na primeira linha para CNPJ/Processo (aceita sinônimos acima)
 Se não encontrar, faz varredura por células com regex para CNPJ e Processo

## Observações
