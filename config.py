import os

# Função simples para carregar variáveis de um arquivo .env (sem depender de bibliotecas externas)
def load_env_from_file():
    try:
        if os.path.exists('.env'):
            with open('.env', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"\'')
    except Exception:
        pass  # Ignora erros ao carregar .env

# Tenta carregar variáveis do .env
load_env_from_file()

# Configuração do banco de dados - usa a variável de ambiente DATABASE_URL
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')

# Configuração do secret key para sessões Flask
SECRET_KEY = os.environ.get('SECRET_KEY', 'uma_chave_secreta_para_desenvolvimento_local')

# Configurações adicionais do SQLAlchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}