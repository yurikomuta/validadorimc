#!/usr/bin/env python3
"""
Script para iniciar a aplicação de validação de código Python.
Este script facilita a execução em ambientes locais.
"""

import os
from main import app

if __name__ == "__main__":
    # Definir host e porta padrão, com opção de sobrescrever por variáveis de ambiente
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "true").lower() == "true"
    
    print(f"Iniciando aplicação no endereço http://{host}:{port}")
    print("Use Ctrl+C para encerrar o servidor")
    
    # Iniciar o servidor Flask
    app.run(host=host, port=port, debug=debug)