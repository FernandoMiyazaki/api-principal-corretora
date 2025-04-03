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
    
    def to_dict(self):
        """
        Retorna uma representação do usuário em forma de dicionário para serialização
        """
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'email': self.email,
            'cpf': self.cpf,
            'cep': self.cep,
            'logradouro': self.logradouro,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'localidade': self.localidade,
            'estado': self.estado,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


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
    
    def to_dict(self):
        """
        Retorna uma representação da transação em forma de dicionário para serialização
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tipo': self.tipo,
            'quantidade_usd': self.quantidade_usd,
            'valor_brl': self.valor_brl,
            'cotacao': self.cotacao,
            'data_transacao': self.data_transacao.strftime('%Y-%m-%d %H:%M:%S') if self.data_transacao else None
        }