import datetime
from main import db

class CodeAnalysis(db.Model):
    """Model para armazenar resultados de análise de código."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    code_content = db.Column(db.Text, nullable=False)
    is_valid = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text, nullable=True)
    error_line = db.Column(db.Integer, nullable=True)
    
    # Skill level information
    skill_level = db.Column(db.String(50), nullable=True)
    skill_score = db.Column(db.Float, nullable=True)
    
    # IMC analysis information
    is_imc_calculator = db.Column(db.Boolean, default=False)
    imc_critical_criteria = db.Column(db.Boolean, default=False)
    imc_desirable_criteria = db.Column(db.Boolean, default=False)
    imc_level = db.Column(db.String(50), nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<CodeAnalysis {self.filename}>'
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            'id': self.id,
            'filename': self.filename,
            'is_valid': self.is_valid,
            'error_message': self.error_message,
            'error_line': self.error_line,
            'skill_level': self.skill_level,
            'skill_score': self.skill_score,
            'is_imc_calculator': self.is_imc_calculator,
            'imc_critical_criteria': self.imc_critical_criteria,
            'imc_desirable_criteria': self.imc_desirable_criteria,
            'imc_level': self.imc_level,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }