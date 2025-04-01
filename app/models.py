from datetime import datetime
from .extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    logradouro = db.Column(db.String(100), nullable=False)
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(50), nullable=False)
    localidade = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    transacoes = db.relationship('Transacao', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.nome_completo}>"


class Transacao(db.Model):
    __tablename__ = 'transacoes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'compra' ou 'venda'
    quantidade_usd = db.Column(db.Float, nullable=False)
    valor_brl = db.Column(db.Float, nullable=False)
    cotacao = db.Column(db.Float, nullable=False)
    data_transacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transacao {self.id} - {self.tipo}>"