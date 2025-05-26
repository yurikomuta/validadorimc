import ast
import io
import sys
import tokenize
import re
from collections import defaultdict

def validate_python_code(code, python_version="3"):
    """
    Validate Python code syntax.
    
    Args:
        code (str): The Python code to validate
        python_version (str): The Python version to validate against (2 or 3)
        
    Returns:
        dict: A dictionary containing validation results
    """
    result = {
        "valid": False,
        "error_message": "",
        "error_line": -1,
    }
    
    # Check if code is empty or whitespace only
    if not code or code.strip() == "":
        result["error_message"] = "O código está vazio."
        result["skill_level"] = {
            "level": "Vazio",
            "score": 0,
            "features": {},
            "imc_analysis": {
                "is_imc_calculator": False,
                "has_functional_calculation": False,
                "has_classification": False,
                "level": "Não Atende Critérios"
            }
        }
        return result
    
    try:
        # Try to parse the code using AST
        ast.parse(code)
        
        # If we got here, the syntax is valid
        result["valid"] = True
        
        # Calculate programming skill level
        skill_level = analyze_skill_level(code)
        result["skill_level"] = skill_level
        
        return result
    
    except SyntaxError as e:
        # Get the error details
        result["error_message"] = str(e)
        result["error_line"] = e.lineno
        
        # Even for invalid code, we want to provide a skill level
        result["skill_level"] = {
            "level": "Com Erros",
            "score": 25,  # 25 points for code with syntax errors
            "features": {},
            "imc_analysis": {
                "is_imc_calculator": detect_imc_calculator(code),
                "has_functional_calculation": False,
                "has_classification": False,
                "level": "Não Atende Critérios"
            }
        }
        
        return result
    
    except Exception as e:
        # Handle other potential errors
        result["error_message"] = f"Unexpected error: {str(e)}"
        
        # Provide basic skill level for unknown errors
        result["skill_level"] = {
            "level": "Com Erros",
            "score": 25,
            "features": {},
            "imc_analysis": {
                "is_imc_calculator": False,
                "has_functional_calculation": False,
                "has_classification": False,
                "level": "Não Atende Critérios"
            }
        }
        
        return result
        
def analyze_skill_level(code):
    """
    Analyze the skill level of the Python code.
    
    Args:
        code (str): The Python code to analyze
        
    Returns:
        dict: A dictionary containing skill level assessment
    """
    result = {
        "level": "Iniciante",
        "score": 0,
        "features": {},
        "imc_analysis": {
            "is_imc_calculator": False,
            "has_functional_calculation": False, 
            "has_classification": False,
            "level": "Não Atende Critérios"
        }
    }
    
    # Parse the code
    try:
        tree = ast.parse(code)
        
        # Count various programming constructs
        features = {
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "comprehensions": 0,
            "error_handling": 0,
            "advanced_types": 0,
            "docstrings": 0,
            "decorators": 0,
            "complex_structures": 0,
            "advanced_features": 0
        }
        
        # Analysis variables
        lines_of_code = len(code.split('\n'))
        
        # Check if this code is an IMC calculator
        # We'll do this by analyzing code structure and keywords
        is_imc_calculator = detect_imc_calculator(code)
        has_functional_calculation = detect_functional_imc_calculation(code)
        has_classification = detect_imc_classification(code)
        
        # Walk through the AST to count features
        for node in ast.walk(tree):
            # Count functions
            if isinstance(node, ast.FunctionDef):
                features["functions"] += 1
                
                # Check for docstrings in functions
                if (node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Str)):
                    features["docstrings"] += 1
                    
                # Check for decorators
                if node.decorator_list:
                    features["decorators"] += 1
                    
            # Count classes
            elif isinstance(node, ast.ClassDef):
                features["classes"] += 1
                
                # Check for docstrings in classes
                if (node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Str)):
                    features["docstrings"] += 1
                    
                # Check for decorators on classes
                if node.decorator_list:
                    features["decorators"] += 1
                    
            # Count imports
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                features["imports"] += 1
                
            # Count list/dict/set comprehensions
            elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                features["comprehensions"] += 1
                
            # Count try/except blocks (error handling)
            elif isinstance(node, ast.Try):
                features["error_handling"] += 1
                
            # Count advanced types (sets, generators)
            elif isinstance(node, (ast.Set, ast.GeneratorExp)):
                features["advanced_types"] += 1
                
            # Count complex data structures
            elif isinstance(node, (ast.Dict, ast.List)) and len(getattr(node, 'keys', lambda: [])() or getattr(node, 'elts', [])) > 5:
                features["complex_structures"] += 1
                
            # Count advanced features
            elif isinstance(node, (ast.AsyncFunctionDef, ast.Await, ast.AsyncFor, ast.AsyncWith, ast.YieldFrom)):
                features["advanced_features"] += 1
        
        # Determine if code is empty
        is_empty = lines_of_code <= 1 or (lines_of_code <= 3 and features["functions"] == 0)
        
        # Calculate special score based on criteria
        score = 0
        
        # Check if it's an IMC calculator
        if detect_imc_calculator(code):
            # IMC calculator-specific scoring
            if has_functional_calculation and has_classification:
                # Desejável - maximum score
                score = 100
                level = "Desejável"
            elif has_functional_calculation:
                # Crítico - medium score
                score = 50
                level = "Crítico"
            else:
                # IMC calculator but with errors - low score
                score = 25
                level = "Com Erros"
        else:
            # General Python code scoring
            if is_empty:
                score = 0
                level = "Vazio"
            else:
                # Calculate traditional score for non-IMC code
                features_score = (
                    features["functions"] * 2 +
                    features["classes"] * 3 +
                    features["imports"] +
                    features["comprehensions"] * 3 +
                    features["error_handling"] * 3 +
                    features["advanced_types"] * 2 +
                    features["docstrings"] * 2 +
                    features["decorators"] * 4 +
                    features["complex_structures"] * 2 +
                    features["advanced_features"] * 5
                )
                
                # Base level on complexity
                if features_score >= 15:
                    level = "Avançado"
                    score = 75
                elif features_score >= 8:
                    level = "Intermediário"
                    score = 50
                else:
                    level = "Iniciante"
                    score = 25
        
        # Determine IMC calculator level
        imc_level = "Não Atende Critérios"
        if is_imc_calculator:
            if has_functional_calculation and has_classification:
                imc_level = "Desejável"
            elif has_functional_calculation:
                imc_level = "Crítico"
                
        # Update the result
        result["score"] = score
        result["level"] = level
        result["features"] = features
        result["imc_analysis"] = {
            "is_imc_calculator": is_imc_calculator,
            "has_functional_calculation": has_functional_calculation,
            "has_classification": has_classification,
            "level": imc_level
        }
        
    except Exception as e:
        # In case of error in analysis, return basic level
        pass
        
    return result

def detect_imc_calculator(code):
    """
    Detect if the code is likely an IMC calculator.
    
    Args:
        code (str): The Python code to analyze
        
    Returns:
        bool: True if the code appears to be an IMC calculator, False otherwise
    """
    code_lower = code.lower()
    
    # Check for IMC-related keywords
    imc_keywords = [
        'imc', 'índice de massa corporal', 'indice de massa corporal', 
        'massa corporal', 'body mass index', 'bmi',
        'peso / (altura', 'peso/(altura', 'peso/(altura * altura)',
        'peso / (altura * altura)', 'peso/altura**2', 'peso / altura**2',
        'weight / (height', 'weight/(height'
    ]
    
    # Check if any of the IMC keywords are in the code
    for keyword in imc_keywords:
        if keyword in code_lower:
            return True
    
    return False

def detect_functional_imc_calculation(code):
    """
    Detect if the code has a functional IMC calculation.
    
    Args:
        code (str): The Python code to analyze
        
    Returns:
        bool: True if the code has a functional IMC calculation, False otherwise
    """
    code_lower = code.lower()
    
    # Check for float conversions for inputs
    has_float_conversion = 'float' in code_lower
    
    # Check for the IMC formula or variations
    formula_patterns = [
        'peso / (altura', 'peso/(altura',
        'peso / altura**2', 'peso/altura**2',
        'peso / (altura * altura)', 'peso/(altura*altura)',
        'weight / (height', 'weight/(height',
        'imc = peso', 'bmi = weight'
    ]
    
    # Check if we have a proper calculation
    has_calculation = False
    for pattern in formula_patterns:
        if pattern in code_lower:
            has_calculation = True
            break
            
    # Make sure print or return is used to show the result
    has_output = 'print' in code_lower or 'return' in code_lower
    
    return has_float_conversion and has_calculation and has_output

def detect_imc_classification(code):
    """
    Detect if the code includes IMC classification.
    
    Args:
        code (str): The Python code to analyze
        
    Returns:
        bool: True if the code includes IMC classification, False otherwise
    """
    code_lower = code.lower()
    
    # Check for classification-related keywords and patterns
    classification_keywords = [
        'abaixo do peso', 'peso normal', 'sobrepeso', 'obesidade',
        'underweight', 'normal weight', 'overweight', 'obesity',
        'if imc <', 'if imc >', 'elif imc', 'if bmi <', 'if bmi >'
    ]
    
    # Check for conditional statements, which are typically used for classification
    has_conditionals = 'if ' in code_lower and (':' in code)
    
    # Check if any of the classification keywords are in the code
    for keyword in classification_keywords:
        if keyword in code_lower:
            return has_conditionals
    
    return False

def suggest_improvements(code):
    """
    Suggest improvements for Python code.
    
    Args:
        code (str): The Python code to analyze
        
    Returns:
        list: A list of improvement suggestions
    """
    suggestions = []
    
    # Check for common issues
    try:
        # Check for long lines
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if len(line) > 79:  # PEP 8 recommendation
                suggestions.append({
                    "line": i + 1,
                    "message": f"Line {i + 1} is too long ({len(line)} characters). Consider breaking it into multiple lines.",
                    "type": "style"
                })
        
        # Check for mixed tabs and spaces
        if '\t' in code and '    ' in code:
            suggestions.append({
                "line": 1,
                "message": "Mixed use of tabs and spaces detected. Stick to using either tabs or spaces for indentation.",
                "type": "style"
            })
        
        # Check for missing docstrings in functions
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not (node.body and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Str)):
                    suggestions.append({
                        "line": node.lineno,
                        "message": f"Function '{node.name}' is missing a docstring.",
                        "type": "documentation"
                    })
            
            # Check for mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in [d for d in node.args.defaults if d]:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        suggestions.append({
                            "line": node.lineno,
                            "message": f"Function '{node.name}' uses a mutable default argument, which can lead to unexpected behavior.",
                            "type": "warning"
                        })
        
        # Check for bare except clauses
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                suggestions.append({
                    "line": node.lineno,
                    "message": "Bare except clause found. It's better to specify which exceptions to catch.",
                    "type": "warning"
                })
        
        # Check for unused imports
        imported_names = set()
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imported_names.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    if name.asname:
                        imported_names.add(name.asname)
                    else:
                        imported_names.add(name.name)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
        
        for unused_import in imported_names - used_names:
            suggestions.append({
                "line": 1,  # We don't have the exact line number here
                "message": f"Unused import: '{unused_import}'",
                "type": "warning"
            })
    
    except Exception as e:
        # If any error occurs during analysis, add it as a note
        suggestions.append({
            "line": 1,
            "message": f"Could not complete full code analysis: {str(e)}",
            "type": "info"
        })
    
    return suggestions
