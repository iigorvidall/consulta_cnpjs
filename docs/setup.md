# Instalação e Execução

## Requisitos
- Python 3.12+
- PostgreSQL (configuração via variáveis de ambiente)
- Dependências Python listadas em `requirements.txt`

## Passos
1. Clonar o repositório e entrar no diretório do projeto
2. Criar e ativar um ambiente virtual
3. Instalar dependências
4. Configurar `.env`
5. Aplicar migrações
6. Rodar o servidor

### Comandos (exemplo)
```powershell
# 1) Clonar
git clone https://github.com/IGNEA-comporativo/Consulta_CNPJ.git
cd Consulta_CNPJ

# 2) Ambiente virtual (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3) Dependências
pip install -r requirements.txt

# 4) Migrações
python manage.py migrate

# 5) Rodar servidor
python manage.py runserver
```

Abra http://127.0.0.1:8000/ no navegador.

Se necessário, ajuste as variáveis no `.env` conforme [configuration.md](configuration.md).