
# Documentação do Validador de Código Python

## 1. Visão Geral do Projeto

Este é um validador de código Python que analisa, pontua e armazena análises de código com foco especial em calculadoras de IMC. O sistema é construído com Flask e utiliza SQLAlchemy para persistência de dados.

## 2. Estrutura Principal

### 2.1 Modelo de Dados (models.py)
```python
class CodeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    code_content = db.Column(db.Text, nullable=False)
    is_valid = db.Column(db.Boolean, default=False)
    skill_level = db.Column(db.String(50), nullable=True)
    skill_score = db.Column(db.Float, nullable=True)
```
Este modelo armazena cada análise de código com seus resultados e metadados.

### 2.2 Sistema de Validação (validator.py)
```python
def validate_python_code(code, python_version="3"):
    result = {
        "valid": False,
        "error_message": "",
        "error_line": -1,
    }
    
    try:
        ast.parse(code)  # Verifica sintaxe
        result["valid"] = True
        result["skill_level"] = analyze_skill_level(code)
        return result
    except SyntaxError as e:
        result["error_message"] = str(e)
        result["error_line"] = e.lineno
        return result
```
O validador analisa a sintaxe do código e atribui pontuações baseadas em critérios específicos.

## 3. Sistema de Pontuação

- **0 pontos**: Código vazio
- **25 pontos**: Código com erros
- **50 pontos**: IMC básico (apenas cálculo)
- **100 pontos**: IMC completo (cálculo + classificação)

### 3.1 Exemplo de Código 100 Pontos
```python
def calcular_imc(peso, altura):
    imc = peso / (altura ** 2)
    
    if imc < 18.5:
        return "Abaixo do peso"
    elif imc < 25:
        return "Peso normal"
    elif imc < 30:
        return "Sobrepeso"
    else:
        return "Obesidade"

# Uso
peso = float(input("Digite seu peso: "))
altura = float(input("Digite sua altura: "))
resultado = calcular_imc(peso, altura)
print(f"Seu IMC indica: {resultado}")
```

## 4. Rotas da Aplicação (routes.py)

### 4.1 Rota Principal
```python
@app.route("/")
def index():
    analyses = CodeAnalysis.query.order_by(
        CodeAnalysis.created_at.desc()
    ).limit(50).all()
    return render_template("index.html", analyses=analyses)
```

### 4.2 Rota de Validação
```python
@app.route("/validate", methods=["POST"])
def validate():
    code = request.form.get("code", "")
    result = validate_python_code(code)
    return jsonify(result)
```

## 5. Interface do Usuário

### 5.1 Template Principal (index.html)
```html
<div class="code-editor">
    <textarea id="code-input" 
              class="form-control" 
              rows="10">
    </textarea>
    <button onclick="validateCode()" 
            class="btn btn-primary">
        Validar Código
    </button>
</div>
```

### 5.2 Visualização de Resultados (view_analysis.html)
```html
<div class="analysis-result">
    <h3>Resultado da Análise</h3>
    <div class="score">
        Pontuação: {{ analysis.skill_score }}
    </div>
    <div class="level">
        Nível: {{ analysis.skill_level }}
    </div>
</div>
```

## 6. Banco de Dados

O sistema utiliza SQLAlchemy e suporta tanto PostgreSQL quanto SQLite:

```python
# Configuração PostgreSQL
SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@localhost/dbname"

# OU SQLite
SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
```

## 7. Funcionalidades Principais

1. **Validação de Sintaxe**
   - Verifica erros no código Python
   - Identifica a linha do erro
   - Fornece mensagens detalhadas

2. **Análise de IMC**
   - Detecta calculadoras de IMC
   - Verifica cálculos corretos
   - Avalia presença de classificação

3. **Sistema de Pontuação**
   - Avalia complexidade do código
   - Considera boas práticas
   - Pontua especificamente IMC

4. **Armazenamento**
   - Salva histórico de análises
   - Permite revisão posterior
   - Exportação de resultados

## 8. Executando o Projeto

```bash
# Iniciar o servidor
python run.py

# Acessar a aplicação
http://0.0.0.0:5000
```

## 9. Dicas de Uso

1. **Upload de Arquivos**
   - Aceita múltiplos arquivos .py
   - Analisa cada arquivo individualmente
   - Fornece relatório consolidado

2. **Editor Online**
   - Syntax highlighting
   - Autocompletion
   - Feedback em tempo real

3. **Histórico**
   - Consulta análises anteriores
   - Filtra por data/pontuação
   - Exporta resultados
