from flask_cors import CORS
from flask_restx import Api

cors = CORS()
api = Api(
    title="API Principal do Sistema de Câmbio",
    version="1.0",
    description="API para gerenciamento de usuários e transações de câmbio",
    doc="/swagger"
)