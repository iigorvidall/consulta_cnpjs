# Interface do Usuário (UI)

A UI principal está em `consulta/templates/consulta/home.html`.

## Entradas
- Campo de CNPJs (manual, separados por vírgula, apenas dígitos, vírgula e espaço)
- Upload de arquivo `csv_file` (.csv/.xlsx)

## Controles do Streaming
- Buscar: inicia o job
- Pausar / Retomar / Cancelar: controlam o job atual
- Indicador de progresso simples (X/Y)

## Tabela de Resultados
- Colunas: Processo, CNPJ, Nome da empresa, E-mail da empresa
- Email exibe “Sem e-mail” quando ausente

## Tabela de Histórico
- Colunas: Data (dd/mm/yy), Processo, CNPJ, Nome, E-mail
- Botões de exportação CSV/XLSX

Notas:
- `table-layout: fixed` é usado para manter largura consistente; texto quebra automaticamente.