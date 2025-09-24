# Consulta CNPJ/CPF

Sistema web para consulta de informações de empresas a partir de CNPJ (e CPF, se implementado), com upload de arquivos CSV/XLSX, histórico de consultas e exportação de resultados.

## Funcionalidades
- Consulta individual ou em lote de CNPJs
- Upload de arquivos CSV/XLSX para consulta em massa
- Delay fixo de 1 segundo entre consultas para evitar bloqueios
- Histórico das consultas realizadas
- Exportação dos resultados e histórico em CSV/XLSX
- Interface web moderna e responsiva

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
- `services.py`: Funções de processamento de CNPJs, integração com API, leitura de arquivos, exportação de dados.
- `views.py`: Lógica das views, controle de fluxo, manipulação de histórico e exportação.
- `models.py`: Modelos do banco de dados (ex: histórico de consultas).
- `home.html`: Interface principal do sistema.

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

## Configurações
- Configure variáveis sensíveis (ex: chaves de API) no arquivo `.env` ou diretamente em `settings.py`.
- O delay entre consultas é fixo em 1 segundo (não configurável na interface).

## Licença
Este projeto é de uso interno IGNEA-comporativo. Para uso externo, consulte o responsável pelo projeto.
