import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define the SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Create the SQLAlchemy instance
db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)

# Carregar configurações do arquivo config.py
app.config.from_pyfile('config.py')

# Para compatibilidade com ambientes que usam SESSION_SECRET
if os.environ.get("SESSION_SECRET"):
    app.secret_key = os.environ.get("SESSION_SECRET")
db.init_app(app)

# Initialize the database
with app.app_context():
    from models import CodeAnalysis
    db.create_all()

# Import and initialize routes
from routes import init_routes
init_routes(app, db)
