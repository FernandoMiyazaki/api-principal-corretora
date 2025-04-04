from flask import request, Blueprint
from flask_restx import Resource, fields
from .extensions import api
from .utils import (
    consultar_api_viacep,
    criar_usuario,
    atualizar_usuario,
    obter_usuario,
    listar_usuarios,
    excluir_usuario,
    consultar_cotacao_dolar,
    registrar_compra_dolar,
    registrar_venda_dolar,
    obter_transacao,
    obter_saldo_usuario
)

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

transaction_model = api.model('Transaction', {
    'id': fields.Integer(readonly=True, description='ID da transação'),
    'user_id': fields.Integer(required=True, description='ID do usuário'),
    'tipo': fields.String(required=True, description='Tipo da transação (compra/venda)'),
    'quantidade_usd': fields.Float(description='Quantidade em USD'),
    'valor_brl': fields.Float(description='Valor em BRL'),
    'cotacao': fields.Float(readonly=True, description='Cotação usada'),
    'data_transacao': fields.DateTime(readonly=True, description='Data e hora da transação')
})

saldo_model = api.model('Saldo', {
    'saldo_usd': fields.Float(description='Saldo em USD')
})


@ns_users.route('/')
class UserList(Resource):
    @ns_users.doc('list_users')
    @ns_users.response(200, 'Sucesso')
    @ns_users.response(500, 'Erro ao listar usuários')
    def get(self):
        """Lista todos os usuários"""
        usuarios = listar_usuarios()
        if usuarios is None:
            return {'message': 'Erro ao obter usuários da API secundária'}, 500
        return usuarios

    @ns_users.doc('create_user',
                params={
                     'nome_completo': 'Nome completo do usuário',
                     'email': 'Email do usuário',
                     'senha': 'Senha do usuário',
                     'cpf': 'CPF do usuário',
                     'cep': 'CEP do usuário',
                     'complemento': 'Complemento do endereço (opcional)'
                })
    @ns_users.response(201, 'Usuário criado com sucesso')
    @ns_users.response(400, 'Dados inválidos')
    @ns_users.response(409, 'Email ou CPF já existente')
    @ns_users.response(500, 'Erro ao criar usuário')
    def post(self):
        """Cria um novo usuário a partir de parâmetros"""
        # Coleta os dados dos parâmetros
        dados_usuario = {
            'nome_completo': request.args.get('nome_completo'),
            'email': request.args.get('email'),
            'senha': request.args.get('senha'),
            'cpf': request.args.get('cpf'),
            'cep': request.args.get('cep'),
            'complemento': request.args.get('complemento', '')
        }
        
        # Verifica se os campos obrigatórios estão presentes
        for campo in ['nome_completo', 'email', 'senha', 'cpf', 'cep']:
            if not dados_usuario.get(campo):
                return {'message': f'Campo obrigatório ausente: {campo}'}, 400
        
        # Envia para a API secundária
        resultado = criar_usuario(dados_usuario)
        if resultado is None:
            return {'message': 'Erro ao criar usuário na API secundária'}, 500
        
        if 'message' in resultado:
            # Se a API secundária retornou um erro
            return resultado, 400 if 'inválido' in resultado['message'] else 409
        
        return resultado, 201


@ns_users.route('/<int:id>')
@ns_users.response(404, 'Usuário não encontrado')
@ns_users.param('id', 'ID do usuário')
class UserResource(Resource):
    @ns_users.doc('get_user')
    @ns_users.response(200, 'Sucesso')
    @ns_users.response(500, 'Erro ao obter usuário')
    def get(self, id):
        """Obtém os dados de um usuário específico"""
        usuario = obter_usuario(id)
        if usuario is None:
            return {'message': 'Erro ao obter usuário da API secundária'}, 500
        if 'message' in usuario:
            return {'message': 'Usuário não encontrado'}, 404
        return usuario

    @ns_users.doc('update_user',
                params={
                     'nome_completo': 'Nome completo do usuário',
                     'email': 'Email do usuário',
                     'senha': 'Senha do usuário',
                     'cep': 'CEP do usuário',
                     'complemento': 'Complemento do endereço'
                })
    @ns_users.response(200, 'Usuário atualizado')
    @ns_users.response(400, 'Dados inválidos')
    @ns_users.response(404, 'Usuário não encontrado')
    @ns_users.response(409, 'Email já cadastrado para outro usuário')
    @ns_users.response(500, 'Erro ao atualizar usuário')
    def put(self, id):
        """Atualiza os dados de um usuário"""
        # Coleta os dados dos parâmetros
        dados_usuario = {}
        for campo in ['nome_completo', 'email', 'senha', 'cep', 'complemento']:
            valor = request.args.get(campo)
            if valor is not None:
                dados_usuario[campo] = valor
        
        # Envia para a API secundária
        resultado = atualizar_usuario(id, dados_usuario)
        if resultado is None:
            return {'message': 'Erro ao atualizar usuário na API secundária'}, 500
        
        if 'message' in resultado:
            if 'não encontrado' in resultado['message']:
                return resultado, 404
            elif 'inválido' in resultado['message']:
                return resultado, 400
            elif 'já cadastrado' in resultado['message']:
                return resultado, 409
            else:
                return resultado, 500
        
        return resultado

    @ns_users.doc('delete_user')
    @ns_users.response(204, 'Usuário excluído')
    @ns_users.response(404, 'Usuário não encontrado')
    @ns_users.response(500, 'Erro ao excluir usuário')
    def delete(self, id):
        """Exclui um usuário"""
        sucesso = excluir_usuario(id)
        if not sucesso:
            return {'message': 'Erro ao excluir usuário na API secundária'}, 500
        return '', 204


@ns_transactions.route('/compra')
class CompraTransaction(Resource):
    @ns_transactions.doc('comprar_dolar',
                      params={
                          'user_id': 'ID do usuário',
                          'valor_brl': 'Valor em BRL para compra de USD'
                      })
    @ns_transactions.response(201, 'Compra registrada')
    @ns_transactions.response(400, 'Dados inválidos')
    @ns_transactions.response(404, 'Usuário não encontrado')
    @ns_transactions.response(500, 'Erro ao registrar compra')
    def post(self):
        """Registra uma compra de dólares"""
        # Coleta os dados dos parâmetros
        dados_compra = {
            'user_id': request.args.get('user_id'),
            'valor_brl': request.args.get('valor_brl')
        }
        
        # Verifica se os campos obrigatórios estão presentes
        for campo in ['user_id', 'valor_brl']:
            if not dados_compra.get(campo):
                return {'message': f'Campo obrigatório ausente: {campo}'}, 400
        
        # Envia para a API secundária
        resultado = registrar_compra_dolar(dados_compra)
        if resultado is None:
            return {'message': 'Erro ao registrar compra na API secundária'}, 500
        
        if 'message' in resultado:
            if 'não encontrado' in resultado['message']:
                return resultado, 404
            else:
                return resultado, 400
        
        return resultado, 201


@ns_transactions.route('/venda')
class VendaTransaction(Resource):
    @ns_transactions.doc('vender_dolar',
                       params={
                           'user_id': 'ID do usuário',
                           'quantidade_usd': 'Quantidade em USD para vender'
                       })
    @ns_transactions.response(201, 'Venda registrada')
    @ns_transactions.response(400, 'Dados inválidos')
    @ns_transactions.response(404, 'Usuário não encontrado')
    @ns_transactions.response(500, 'Erro ao registrar venda')
    def post(self):
        """Registra uma venda de dólares"""
        # Coleta os dados dos parâmetros
        dados_venda = {
            'user_id': request.args.get('user_id'),
            'quantidade_usd': request.args.get('quantidade_usd')
        }
        
        # Verifica se os campos obrigatórios estão presentes
        for campo in ['user_id', 'quantidade_usd']:
            if not dados_venda.get(campo):
                return {'message': f'Campo obrigatório ausente: {campo}'}, 400
        
        # Envia para a API secundária
        resultado = registrar_venda_dolar(dados_venda)
        if resultado is None:
            return {'message': 'Erro ao registrar venda na API secundária'}, 500
        
        if 'message' in resultado:
            if 'não encontrado' in resultado['message']:
                return resultado, 404
            elif 'insuficiente' in resultado['message']:
                return resultado, 400
            else:
                return resultado, 400
        
        return resultado, 201


@ns_transactions.route('/<int:id>')
@ns_transactions.response(404, 'Transação não encontrada')
@ns_transactions.param('id', 'ID da transação')
class TransactionResource(Resource):
    @ns_transactions.doc('get_transaction')
    @ns_transactions.response(200, 'Sucesso')
    @ns_transactions.response(500, 'Erro ao obter transação')
    def get(self, id):
        """Obtém os dados de uma transação específica"""
        transacao = obter_transacao(id)
        if transacao is None:
            return {'message': 'Erro ao obter transação da API secundária'}, 500
        if 'message' in transacao:
            return {'message': 'Transação não encontrada'}, 404
        return transacao


@ns_users.route('/<int:id>/saldo')
@ns_users.response(404, 'Usuário não encontrado')
@ns_users.param('id', 'ID do usuário')
class UserBalance(Resource):
    @ns_users.doc('get_user_balance')
    @ns_users.response(200, 'Sucesso')
    @ns_users.response(500, 'Erro ao obter saldo')
    def get(self, id):
        """Obtém o saldo em USD do usuário"""
        saldo = obter_saldo_usuario(id)
        if saldo is None:
            return {'message': 'Erro ao obter saldo da API secundária'}, 500
        if 'message' in saldo:
            return {'message': 'Usuário não encontrado'}, 404
        return saldo