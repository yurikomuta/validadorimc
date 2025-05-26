#!/usr/bin/env python3
"""
Script para configuração inicial do ambiente local.
Executa as tarefas básicas para preparar o projeto para execução.
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Verifica se a versão do Python é adequada."""
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 7):
        print("ERRO: Este projeto requer Python 3.7 ou superior.")
        print(f"Você está usando Python {version_info.major}.{version_info.minor}")
        sys.exit(1)
    print(f"✓ Usando Python {version_info.major}.{version_info.minor}.{version_info.micro}")

def setup_env_file():
    """Configura o arquivo .env se não existir."""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✓ Arquivo .env criado com base no exemplo")
            print("  IMPORTANTE: Edite o arquivo .env com suas configurações")
        else:
            with open('.env', 'w') as f:
                f.write("# Configuração automática\n")
                f.write("DATABASE_URL=sqlite:///app.db\n")
                f.write(f"SECRET_KEY={''.join('%02x' % i for i in os.urandom(16))}\n")
            print("✓ Arquivo .env criado com configurações básicas (SQLite)")
    else:
        print("✓ Arquivo .env já existe")

def check_database():
    """Verifica a configuração do banco de dados."""
    try:
        import config
        db_url = config.SQLALCHEMY_DATABASE_URI
        
        if db_url.startswith('sqlite'):
            print(f"✓ Usando banco de dados SQLite: {db_url.split('///')[1]}")
        elif db_url.startswith('postgresql'):
            print(f"✓ Usando banco de dados PostgreSQL")
            # Aqui poderia verificar a conexão com o PostgreSQL
        else:
            print(f"! Usando outro banco de dados: {db_url.split('://')[0]}")
            
    except ImportError:
        print("! Não foi possível importar a configuração do banco de dados")

def main():
    """Função principal do script."""
    print("\n===== Configuração do Validador de Código Python =====\n")
    
    check_python_version()
    setup_env_file()
    
    print("\nVerificando configuração do banco de dados...")
    check_database()
    
    print("\nPara iniciar o aplicativo, execute:")
    print("  python run.py")
    print("\nPara mais informações, consulte README.md e SETUP_LOCAL.md")
    print("\n=====================================================\n")

if __name__ == "__main__":
    main()