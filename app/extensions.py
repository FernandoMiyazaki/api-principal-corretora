from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restx import Api

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
api = Api(
    title="API Principal do Sistema de Câmbio",
    version="1.0",
    description="API para gerenciamento de usuários e transações de câmbio",
    doc="/swagger"
)