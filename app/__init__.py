import os
from flask import Flask
from .extensions import cors, api
from .routes import main, ns_users, ns_transactions
from .config import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializa extensões
    cors.init_app(app)
    
    # Registra blueprints
    app.register_blueprint(main)
    
    # Inicializa API com Swagger
    api.init_app(app)
    
    # Adiciona namespaces à API
    api.add_namespace(ns_users)
    api.add_namespace(ns_transactions)
    
    return app