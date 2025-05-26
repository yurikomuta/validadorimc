# Validador de Código Python

Um sistema web para validação e análise de código Python, com ênfase em avaliação de habilidades de programação e análise específica para calculadoras de IMC (Índice de Massa Corporal).

## Funcionalidades

- Verificação de sintaxe de código Python
- Análise automática do nível de programação
- Detecção de características de código avançadas
- Avaliação específica para calculadoras de IMC
- Sistema de pontuação:
  - 0 pontos: Código vazio
  - 25 pontos: Código com erros de sintaxe
  - 50 pontos: Calculadora IMC funcional (critério crítico)
  - 100 pontos: Calculadora IMC completa com classificação (critério desejável)
- Suporte para upload de múltiplos arquivos
- Armazenamento de análises em banco de dados
- Exportação de resultados para CSV

## Requisitos

- Python 3.9 ou superior
- PostgreSQL (ou SQLite como alternativa)
- Bibliotecas Python conforme requirements.txt

## Instalação

1. Clone o repositório ou baixe o código fonte
2. Crie um ambiente virtual Python:
   ```bash
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Unix/macOS: `source venv/bin/activate`
4. Instale as dependências:
   ```bash
   pip install flask flask-sqlalchemy email-validator gunicorn psycopg2-binary
   ```
5. Configure o banco de dados (veja SETUP_LOCAL.md para mais detalhes)
6. Execute o servidor:
   ```bash
   python run.py
   ```

Para instruções mais detalhadas, consulte o arquivo [SETUP_LOCAL.md](SETUP_LOCAL.md).

## Execução

Após a instalação, você pode executar o servidor com:
```bash
python run.py
```

Acesse a aplicação em: http://localhost:5000

## Estrutura do Projeto

- `main.py`: Entrada principal da aplicação
- `app.py`: Configuração do app Flask
- `models.py`: Definição dos modelos de dados
- `routes.py`: Definição das rotas da aplicação
- `validator.py`: Lógica de validação de código Python
- `config.py`: Configurações do projeto
- `templates/`: Arquivos HTML
- `static/`: Arquivos estáticos (CSS, JavaScript)

## Sistema de Pontuação

- **0 pontos**: Arquivo vazio ou apenas com comentários
- **25 pontos**: Código com erros de sintaxe ou incompleto
- **50 pontos**: Calculadora IMC que atende ao critério crítico (cálculo funcional)
- **100 pontos**: Calculadora IMC que atende ao critério desejável (cálculo + classificação)

Para código que não é uma calculadora IMC, a pontuação é baseada em sua complexidade.

## Exportação de Dados

A aplicação permite exportar as análises armazenadas para arquivo CSV através do botão "Exportar para CSV" nas tabelas de resultados.