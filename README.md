
# Consulta CNPJ/CPF

## Documentação Completa
Para detalhes de arquitetura, API, configuração, importação/exportação, FAQ e troubleshooting, acesse:

- [Documentação detalhada (docs/index.md)](docs/index.md)

Principais tópicos:
- Visão Geral
- Instalação e Execução
- Configuração e Variáveis de Ambiente
- Arquitetura e Componentes
- API (REST e Streaming)
- Interface do Usuário (UI)
- Modelo de Dados (Histórico)
- Importação de Arquivos (CSV/XLSX)
- Exportação (CSV/XLSX)
- Operação e Resiliência
- Solução de Problemas
- FAQ

Sistema web em Django para consultar informações de empresas (CNPJ) utilizando a API CNPJÁ PRO. Suporta upload CSV/XLSX, fluxo de processamento “streaming” com pausa/retomada/cancelamento, histórico sem horário e exportação incluindo o número do processo vinculado.

## Funcionalidades
- Consulta individual ou em lote (CSV/XLSX)
- Fluxo “streaming” com controle: Pausar, Retomar e Cancelar
- Suporte ao campo Processo em todo o fluxo (entrada, resultados, histórico e exportações)
- Delay fixo de 1 segundo entre consultas (ajustável no código) para respeitar limites
- Estratégia de cache do CNPJÁ configurável (strategy, maxAge, maxStale)
- Histórico de consultas com data no formato dd/mm/yy (sem horário)
- Exportação de resultados e histórico em CSV/XLSX, incluindo Processo
- Parser robusto para CSV/XLSX (detecta colunas ou faz varredura por CNPJ)
- Tratamento de e-mail ausente exibindo “Sem e-mail”
- DRF endpoint para JSON completo por CNPJ e limitação global de 100/min

## Estrutura do Projeto
```
manage.py
consulta/
    __init__.py
    admin.py
    apps.py
    forms.py
    models.py
   services.py
    tests.py
    urls.py
    views.py
    migrations/
    templates/
        consulta/
            home.html
consulta_cnpj_cpf/
    __init__.py
    asgi.py
    settings.py
    urls.py
    wsgi.py
```

## Principais Módulos
- `clients/cnpja.py`: Cliente HTTP para a API CNPJÁ PRO, incluindo parâmetros de cache (strategy, maxAge, maxStale).
- `consulta/services.py`: Regras de negócio (consulta à API com retry e cache, parsing CSV/XLSX, exportação CSV/XLSX). DELAY_SECONDS controla o intervalo entre chamadas (padrão 1s).
- `consulta/views.py`: Views web e endpoints “jobs_*” do fluxo de streaming; persistência do histórico; exportações via services.
- `consulta/models.py`: Modelo `ConsultaHistorico` com armazenamento do resultado da execução.
- `consulta/templates/consulta/home.html`: UI principal (upload/entrada manual, controles de streaming, tabelas de Resultados e Histórico).

## Como rodar localmente
1. Clone o repositório:
   ```
   git clone https://github.com/IGNEA-comporativo/Consulta_CNPJ.git
   cd Consulta_CNPJ
   ```
2. Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   # ou
   source venv/bin/activate  # Linux/Mac
   ```
3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
4. Realize as migrações:
   ```
   python manage.py migrate
   ```
5. Rode o servidor:
   ```
   python manage.py runserver
   ```

### DRF e Rate Limiting
- DRF habilitado e com limite global de 100/min para anônimo e usuário (`consulta_cnpj_cpf/settings.py`).

Observações:
- O campo “Processo” é suportado em uploads (CSV/XLSX) quando existir coluna correspondente (ex.: `processo`, `número do processo`); o sistema aceita CNPJs repetidos com processos diferentes.
- Em caso de arquivos caóticos, o sistema tenta extrair CNPJs via regex mesmo sem cabeçalhos válidos.
- Exportações (CSV/XLSX) incluem a coluna “Processo”. No histórico, a data é exibida como dd/mm/yy.

## Licença
Projeto de uso interno IGNEA-comporativo. Para uso externo, consulte o responsável pelo projeto.
