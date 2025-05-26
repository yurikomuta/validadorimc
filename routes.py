import logging
from flask import render_template, request, jsonify, redirect, url_for
from models import CodeAnalysis
from validator import validate_python_code, suggest_improvements

def init_routes(app, db):
    """Initialize all routes for the application."""
    
    @app.route("/")
    def index():
        """Render the main page."""
        # Recuperar a lista de análises anteriores para exibir na tabela
        analyses = CodeAnalysis.query.order_by(CodeAnalysis.created_at.desc()).limit(50).all()
        return render_template("index.html", analyses=analyses)
    
    @app.route("/validate", methods=["POST"])
    def validate():
        """
        Validate the Python code submitted by the user.
        The code can be submitted either as text or as a file.
        """
        try:
            # Get the Python version from the request
            python_version = request.form.get("python_version", "3")
            
            # Checar se são múltiplos arquivos
            files = request.files.getlist('file')
            
            # Se tiver arquivos, processa cada um deles
            if files and files[0].filename:
                results = []
                for file in files:
                    # Read the content of the file
                    code = file.read().decode('utf-8')
                    filename = file.filename
                    
                    # Process this file
                    result = process_and_save_code(code, filename, python_version, db)
                    results.append(result)
                
                # Return the results for all files
                return jsonify({
                    "multi_file": True,
                    "results": results
                })
            else:
                # Processar código direto do textarea
                code = request.form.get("code", "")
                filename = "code_snippet.py"
                
                # Process this single code snippet
                result = process_and_save_code(code, filename, python_version, db)
                
                # For backward compatibility, return a single result
                return jsonify(result)
        
        except Exception as e:
            logging.error(f"Error during validation: {str(e)}")
            return jsonify({
                "valid": False,
                "error_message": f"Internal server error: {str(e)}",
                "error_line": -1,
                "suggestions": []
            })
    
    @app.route("/analyses")
    def list_analyses():
        """List all saved code analyses."""
        analyses = CodeAnalysis.query.order_by(CodeAnalysis.created_at.desc()).all()
        return render_template("analyses.html", analyses=analyses)
    
    @app.route("/analysis/<int:analysis_id>")
    def view_analysis(analysis_id):
        """View a specific code analysis."""
        analysis = CodeAnalysis.query.get_or_404(analysis_id)
        return render_template("view_analysis.html", analysis=analysis)

    @app.route("/analysis/<int:analysis_id>/delete", methods=["POST"])
    def delete_analysis(analysis_id):
        """Delete a specific code analysis."""
        analysis = CodeAnalysis.query.get_or_404(analysis_id)
        db.session.delete(analysis)
        db.session.commit()
        return redirect(url_for("list_analyses"))
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors."""
        return render_template('index.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors."""
        return render_template('index.html'), 500

def process_and_save_code(code, filename, python_version, db):
    """Process the code and save the results to the database."""
    # Validate the code
    validation_result = validate_python_code(code, python_version)
    
    # Get improvement suggestions if syntax is valid
    suggestions = []
    if validation_result["valid"]:
        suggestions = suggest_improvements(code)
    
    # Prepare response data
    response_data = {
        "valid": validation_result["valid"],
        "error_message": validation_result["error_message"],
        "error_line": validation_result["error_line"],
        "filename": filename,
        "suggestions": suggestions
    }
    
    # Add skill level information - now available for both valid and invalid code
    if "skill_level" in validation_result:
        response_data["skill_level"] = validation_result["skill_level"]
        
        # Create a database record for this analysis
        analysis = CodeAnalysis(
            filename=filename,
            code_content=code,
            is_valid=validation_result["valid"],
            error_message=validation_result["error_message"],
            error_line=validation_result["error_line"],
            skill_level=validation_result["skill_level"]["level"],
            skill_score=validation_result["skill_level"]["score"]
        )
        
        # Add IMC-specific information if available
        if "imc_analysis" in validation_result["skill_level"]:
            imc_analysis = validation_result["skill_level"]["imc_analysis"]
            analysis.is_imc_calculator = imc_analysis["is_imc_calculator"]
            analysis.imc_critical_criteria = imc_analysis["has_functional_calculation"]
            analysis.imc_desirable_criteria = imc_analysis["has_classification"]
            analysis.imc_level = imc_analysis["level"]
        
        # Save to database
        db.session.add(analysis)
        db.session.commit()
        
        # Add the database ID to the response
        response_data["analysis_id"] = analysis.id
        
    return response_data