import requests
from flask import current_app


def consultar_api_viacep(cep):
    """
    Consulta a API ViaCEP para obter os dados de endereço com base no CEP
    """
    try:
        api_url = f"{current_app.config['VIACEP_API_URL']}/cep/{cep}"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao consultar API ViaCEP: {str(e)}")
        return None


def criar_usuario(dados_usuario):
    """
    Envia uma requisição para a API ViaCEP para criar um novo usuário
    """
    try:
        # Constrói a URL com os parâmetros
        api_url = f"{current_app.config['VIACEP_API_URL']}/usuarios"
        params = {
            'nome_completo': dados_usuario.get('nome_completo'),
            'email': dados_usuario.get('email'),
            'senha': dados_usuario.get('senha'),
            'cpf': dados_usuario.get('cpf'),
            'cep': dados_usuario.get('cep'),
            'complemento': dados_usuario.get('complemento', '')
        }
        
        response = requests.post(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao criar usuário na API ViaCEP: {str(e)}")
        return None


def atualizar_usuario(user_id, dados_usuario):
    """
    Envia uma requisição para a API ViaCEP para atualizar um usuário existente
    """
    try:
        # Constrói a URL com os parâmetros
        api_url = f"{current_app.config['VIACEP_API_URL']}/usuarios/{user_id}"
        params = {}
        
        # Adiciona apenas os campos fornecidos
        if 'nome_completo' in dados_usuario:
            params['nome_completo'] = dados_usuario['nome_completo']
        if 'email' in dados_usuario:
            params['email'] = dados_usuario['email']
        if 'senha' in dados_usuario:
            params['senha'] = dados_usuario['senha']
        if 'cep' in dados_usuario:
            params['cep'] = dados_usuario['cep']
        if 'complemento' in dados_usuario:
            params['complemento'] = dados_usuario['complemento']
        
        response = requests.put(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao atualizar usuário na API ViaCEP: {str(e)}")
        return None


def obter_usuario(user_id):
    """
    Obtém os dados de um usuário específico da API ViaCEP
    """
    try:
        api_url = f"{current_app.config['VIACEP_API_URL']}/usuarios/{user_id}"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao obter usuário da API ViaCEP: {str(e)}")
        return None


def listar_usuarios():
    """
    Lista todos os usuários da API ViaCEP
    """
    try:
        api_url = f"{current_app.config['VIACEP_API_URL']}/usuarios"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao listar usuários da API ViaCEP: {str(e)}")
        return None


def excluir_usuario(user_id):
    """
    Exclui um usuário da API ViaCEP
    """
    try:
        api_url = f"{current_app.config['VIACEP_API_URL']}/usuarios/{user_id}"
        response = requests.delete(api_url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao excluir usuário da API ViaCEP: {str(e)}")
        return False


def consultar_cotacao_dolar():
    """
    Consulta a API Frankfurter para obter a cotação atual do dólar em BRL
    """
    try:
        api_url = f"{current_app.config['FRANKFURTER_API_URL']}/cotacao"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao consultar API Frankfurter: {str(e)}")
        return None


def registrar_compra_dolar(dados_compra):
    """
    Envia uma requisição para a API Frankfurter para registrar uma compra de dólares
    """
    try:
        api_url = f"{current_app.config['FRANKFURTER_API_URL']}/transacoes/compra"
        params = {
            'user_id': dados_compra.get('user_id'),
            'valor_brl': dados_compra.get('valor_brl')
        }
        
        response = requests.post(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao registrar compra na API Frankfurter: {str(e)}")
        return None


def registrar_venda_dolar(dados_venda):
    """
    Envia uma requisição para a API Frankfurter para registrar uma venda de dólares
    """
    try:
        api_url = f"{current_app.config['FRANKFURTER_API_URL']}/transacoes/venda"
        params = {
            'user_id': dados_venda.get('user_id'),
            'quantidade_usd': dados_venda.get('quantidade_usd')
        }
        
        response = requests.post(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao registrar venda na API Frankfurter: {str(e)}")
        return None


def obter_transacao(transaction_id):
    """
    Obtém os dados de uma transação específica da API Frankfurter
    """
    try:
        api_url = f"{current_app.config['FRANKFURTER_API_URL']}/transacoes/{transaction_id}"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao obter transação da API Frankfurter: {str(e)}")
        return None


def obter_saldo_usuario(user_id):
    """
    Obtém o saldo de um usuário da API Frankfurter
    """
    try:
        api_url = f"{current_app.config['FRANKFURTER_API_URL']}/transacoes/usuario/{user_id}/saldo"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao obter saldo da API Frankfurter: {str(e)}")
        return None