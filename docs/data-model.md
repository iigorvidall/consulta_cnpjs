# Modelo de Dados (Histórico)

O histórico é persistido via modelo `ConsultaHistorico` (app `consulta`). O campo `resultado` armazena a lista de itens retornados no job.

## Estrutura típica de um item de resultado
```
{
  "cnpj": "00.000.000/0000-00",
  "nome": "Empresa XYZ LTDA",
  "email": "contato@..." | "Sem e-mail" | "-" | "Erro: ...",
  "processo": "12345/2025" | null
}
```

## Exportações
- CSV/XLSX de resultados: colunas [Processo, CNPJ, Nome, E-mail]
- CSV/XLSX de histórico: colunas [Data (dd/mm/yy), Processo, CNPJ, Nome, E-mail]

Observações:
- E-mails ausentes são normalizados para “Sem e-mail” nas exportações.