# Configuração do Projeto Python Validator

Este arquivo contém instruções para configurar e executar o projeto em sua máquina local.

## Requisitos

- Python 3.9 ou superior
- PostgreSQL (ou SQLite como alternativa mais simples)
- pip (gerenciador de pacotes Python)

## Passos para Configuração

### 1. Preparar o ambiente Python

```bash
# Criar um ambiente virtual
python -m venv venv

# Ativar o ambiente virtual (Windows)
venv\Scripts\activate

# Ativar o ambiente virtual (Mac/Linux)
source venv/bin/activate

# Instalar as dependências
pip install flask flask-sqlalchemy email-validator gunicorn psycopg2-binary python-dotenv
```

### 2. Configurar o Banco de Dados

#### Opção A: PostgreSQL (Recomendado)

1. Instale o PostgreSQL de [postgresql.org](https://www.postgresql.org/download/)
2. Crie um banco de dados:
   ```sql
   CREATE DATABASE python_validator;
   ```
3. Crie um arquivo `.env` na raiz do projeto:
   ```
   DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost/python_validator
   ```

#### Opção B: SQLite (Alternativa mais simples)

Crie um arquivo `.env` na raiz do projeto:
```
DATABASE_URL=sqlite:///app.db
```

### 3. Configurar a Aplicação

Crie um arquivo `config.py` na raiz do projeto:

```python
import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Configuração do banco de dados
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

### 4. Inicializar o Banco de Dados

```bash
# Abra o Python interativo
python

# No console do Python, execute:
from app import app, db
with app.app_context():
    db.create_all()
exit()
```

### 5. Executar a Aplicação

```bash
# Usando Flask diretamente
flask run

# OU usando Gunicorn
python -m gunicorn --bind 0.0.0.0:5000 main:app
```

Acesse a aplicação em: http://localhost:5000

## Estrutura de Arquivos

- `main.py`: Ponto de entrada da aplicação
- `app.py`: Configuração da aplicação Flask e do banco de dados
- `models.py`: Modelos de dados
- `routes.py`: Rotas e lógica da aplicação
- `validator.py`: Lógica de validação de código Python
- `templates/`: Arquivos HTML
- `static/`: Arquivos CSS, JavaScript, imagens, etc.

## Solução de Problemas

- Se encontrar erros de módulos não encontrados, verifique se todas as dependências foram instaladas corretamente.
- Se tiver problemas com o PostgreSQL, tente usar SQLite como alternativa temporária.
- Para visualizar os logs da aplicação, execute-a com o modo de debug ativado:
  ```bash
  FLASK_DEBUG=1 flask run
  ```

## Backup e Restauração do Banco de Dados

Para exportar o banco de dados PostgreSQL:
```bash
pg_dump -U seu_usuario python_validator > backup.sql
```

Para importar o banco de dados:
```bash
psql -U seu_usuario python_validator < backup.sql
```