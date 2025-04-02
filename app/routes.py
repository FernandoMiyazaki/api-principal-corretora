from flask import request, jsonify, Blueprint
from flask_restx import Resource, fields
from sqlalchemy.exc import IntegrityError
from .extensions import db, api
from .models import User, Transacao
from .utils import get_endereco_by_cep, get_cotacao_dolar, calcular_saldo_usd_usuario

# Blueprint
main = Blueprint('main', __name__)

# Namespaces
ns_users = api.namespace('users', description='Operações relacionadas a usuários')
ns_transactions = api.namespace('transactions', description='Operações relacionadas a transações')

# Models
user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='ID único do usuário'),
    'nome_completo': fields.String(required=True, description='Nome completo do usuário'),
    'email': fields.String(required=True, description='Email do usuário'),
    'cpf': fields.String(required=True, description='CPF do usuário'),
    'cep': fields.String(required=True, description='CEP do usuário'),
    'complemento': fields.String(description='Complemento do endereço'),
    'logradouro': fields.String(readonly=True, description='Logradouro'),
    'bairro': fields.String(readonly=True, description='Bairro'),
    'localidade': fields.String(readonly=True, description='Cidade'),
    'estado': fields.String(readonly=True, description='Estado')
})

user_input_model = api.model('UserInput', {
    'nome_completo': fields.String(required=True, description='Nome completo do usuário'),
    'email': fields.String(required=True, description='Email do usuário'),
    'senha': fields.String(required=True, description='Senha do usuário'),
    'cpf': fields.String(required=True, description='CPF do usuário'),
    'cep': fields.String(required=True, description='CEP do usuário'),
    'complemento': fields.String(description='Complemento do endereço')
})

user_update_model = api.model('UserUpdate', {
    'nome_completo': fields.String(description='Nome completo do usuário'),
    'email': fields.String(description='Email do usuário'),
    'senha': fields.String(description='Senha do usuário'),
    'cep': fields.String(description='CEP do usuário'),
    'complemento': fields.String(description='Complemento do endereço')
})

transaction_model = api.model('Transaction', {
    'id': fields.Integer(readonly=True, description='ID da transação'),
    'user_id': fields.Integer(required=True, description='ID do usuário'),
    'tipo': fields.String(required=True, description='Tipo da transação (compra/venda)'),
    'quantidade_usd': fields.Float(description='Quantidade em USD'),
    'valor_brl': fields.Float(description='Valor em BRL'),
    'cotacao': fields.Float(readonly=True, description='Cotação usada'),
    'data_transacao': fields.DateTime(readonly=True, description='Data e hora da transação')
})

transaction_input_model = api.model('TransactionInput', {
    'user_id': fields.Integer(required=True, description='ID do usuário'),
    'valor_brl': fields.Float(required=True, description='Valor em BRL para compra de USD')
})

transaction_venda_model = api.model('TransactionVenda', {
    'user_id': fields.Integer(required=True, description='ID do usuário'),
    'quantidade_usd': fields.Float(required=True, description='Quantidade em USD para vender')
})

saldo_usd_model = api.model('SaldoUSD', {
    'saldo_usd': fields.Float(description='Saldo em USD')
})


@ns_users.route('/')
class UserList(Resource):
    @ns_users.doc('list_users')
    @ns_users.marshal_list_with(user_model)
    def get(self):
        """Lista todos os usuários"""
        users = User.query.all()
        return users

    @ns_users.doc('create_user')
    @ns_users.expect(user_input_model)
    @ns_users.response(201, 'Usuário criado com sucesso', user_model)
    @ns_users.response(400, 'Dados inválidos')
    @ns_users.response(409, 'Email ou CPF já existente')
    def post(self):
        """Cria um novo usuário"""
        data = request.json
        
        # Verifica se os campos obrigatórios estão presentes
        required_fields = ['nome_completo', 'email', 'senha', 'cpf', 'cep']
        for field in required_fields:
            if field not in data:
                return {'message': f'Campo obrigatório ausente: {field}'}, 400
        
        # Consulta o CEP na API ViaCEP
        endereco = get_endereco_by_cep(data['cep'])
        if not endereco or 'erro' in endereco:
            return {'message': 'CEP inválido ou não encontrado'}, 400
        
        try:
            novo_usuario = User(
                nome_completo=data['nome_completo'],
                email=data['email'],
                senha=data['senha'],  # Em produção, deve-se usar hash
                cpf=data['cpf'],
                cep=data['cep'],
                logradouro=endereco['logradouro'],
                complemento=data.get('complemento', ''),
                bairro=endereco['bairro'],
                localidade=endereco['localidade'],
                estado=endereco['estado']
            )
            
            db.session.add(novo_usuario)
            db.session.commit()
            
            return novo_usuario, 201
            
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Email ou CPF já cadastrado'}, 409
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao criar usuário: {str(e)}'}, 400


@ns_users.route('/<int:id>')
@ns_users.response(404, 'Usuário não encontrado')
@ns_users.param('id', 'ID do usuário')
class UserResource(Resource):
    @ns_users.doc('get_user')
    @ns_users.marshal_with(user_model)
    def get(self, id):
        """Obtém os dados de um usuário específico"""
        user = User.query.get_or_404(id)
        return user

    @ns_users.doc('update_user')
    @ns_users.expect(user_update_model)
    @ns_users.marshal_with(user_model)
    def put(self, id):
        """Atualiza os dados de um usuário"""
        user = User.query.get_or_404(id)
        data = request.json
        
        # Atualiza os campos fornecidos
        if 'nome_completo' in data:
            user.nome_completo = data['nome_completo']
        if 'email' in data:
            user.email = data['email']
        if 'senha' in data:
            user.senha = data['senha']  # Em produção, deve-se usar hash
        if 'cep' in data:
            # Se o CEP foi atualizado, consulta a API ViaCEP
            endereco = get_endereco_by_cep(data['cep'])
            if not endereco or 'erro' in endereco:
                return {'message': 'CEP inválido ou não encontrado'}, 400
            
            user.cep = data['cep']
            user.logradouro = endereco['logradouro']
            user.bairro = endereco['bairro']
            user.localidade = endereco['localidade']
            user.estado = endereco['estado']
        
        if 'complemento' in data:
            user.complemento = data['complemento']
        
        try:
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Email já cadastrado para outro usuário'}, 409
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao atualizar usuário: {str(e)}'}, 400

    @ns_users.doc('delete_user')
    @ns_users.response(204, 'Usuário excluído')
    def delete(self, id):
        """Exclui um usuário"""
        user = User.query.get_or_404(id)
        
        try:
            db.session.delete(user)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao excluir usuário: {str(e)}'}, 400


@ns_transactions.route('/compra')
class CompraTransaction(Resource):
    @ns_transactions.doc('comprar_dolar')
    @ns_transactions.expect(transaction_input_model)
    @ns_transactions.marshal_with(transaction_model, code=201)
    def post(self):
        """Registra uma compra de dólares"""
        data = request.json
        
        # Verifica se os campos obrigatórios estão presentes
        if 'user_id' not in data or 'valor_brl' not in data:
            return {'message': 'Campos obrigatórios ausentes'}, 400
        
        # Verifica se o usuário existe
        user = User.query.get(data['user_id'])
        if not user:
            return {'message': 'Usuário não encontrado'}, 404
        
        # Obtém a cotação atual do dólar
        cotacao_data = get_cotacao_dolar()
        if not cotacao_data:
            return {'message': 'Erro ao obter cotação do dólar'}, 500
        
        cotacao = cotacao_data['rates']['BRL']
        valor_brl = float(data['valor_brl'])
        quantidade_usd = valor_brl / cotacao
        
        try:
            nova_transacao = Transacao(
                user_id=data['user_id'],
                tipo='compra',
                quantidade_usd=quantidade_usd,
                valor_brl=valor_brl,
                cotacao=cotacao
            )
            
            db.session.add(nova_transacao)
            db.session.commit()
            
            return nova_transacao, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao registrar compra: {str(e)}'}, 400


@ns_transactions.route('/venda')
class VendaTransaction(Resource):
    @ns_transactions.doc('vender_dolar')
    @ns_transactions.expect(transaction_venda_model)
    @ns_transactions.marshal_with(transaction_model, code=201)
    def post(self):
        """Registra uma venda de dólares"""
        data = request.json
        
        # Verifica se os campos obrigatórios estão presentes
        if 'user_id' not in data or 'quantidade_usd' not in data:
            return {'message': 'Campos obrigatórios ausentes'}, 400
        
        # Verifica se o usuário existe
        user = User.query.get(data['user_id'])
        if not user:
            return {'message': 'Usuário não encontrado'}, 404
        
        # Obtém a cotação atual do dólar
        cotacao_data = get_cotacao_dolar()
        if not cotacao_data:
            return {'message': 'Erro ao obter cotação do dólar'}, 500
        
        cotacao = cotacao_data['rates']['BRL']
        quantidade_usd = float(data['quantidade_usd'])
        valor_brl = quantidade_usd * cotacao
        
        # Verifica se o usuário tem saldo em dólares suficiente
        saldo_usd = calcular_saldo_usd_usuario(data['user_id'])
        if saldo_usd < quantidade_usd:
            return {'message': 'Saldo em dólares insuficiente'}, 400
        
        try:
            nova_transacao = Transacao(
                user_id=data['user_id'],
                tipo='venda',
                quantidade_usd=quantidade_usd,
                valor_brl=valor_brl,
                cotacao=cotacao
            )
            
            db.session.add(nova_transacao)
            db.session.commit()
            
            return nova_transacao, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao registrar venda: {str(e)}'}, 400


@ns_transactions.route('/<int:id>')
@ns_transactions.response(404, 'Transação não encontrada')
@ns_transactions.param('id', 'ID da transação')
class TransactionResource(Resource):
    @ns_transactions.doc('get_transaction')
    @ns_transactions.marshal_with(transaction_model)
    def get(self, id):
        """Obtém os dados de uma transação específica"""
        transaction = Transacao.query.get_or_404(id)
        return transaction


@ns_users.route('/<int:id>/saldo')
@ns_users.response(404, 'Usuário não encontrado')
@ns_users.param('id', 'ID do usuário')
class UserBalance(Resource):
    @ns_users.doc('get_user_balance')
    @ns_users.marshal_with(saldo_usd_model)
    def get(self, id):
        """Obtém o saldo em USD do usuário"""
        user = User.query.get_or_404(id)
        saldo_usd = calcular_saldo_usd_usuario(id)
        return {"saldo_usd": saldo_usd}