import requests
from flask import current_app


def get_endereco_by_cep(cep):
    """
    Consulta a API ViaCEP para obter os dados de endereço com base no CEP
    """
    try:
        api_url = f"{current_app.config['VIACEP_API_URL']}/cep/{cep}"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao consultar ViaCEP: {str(e)}")
        return None


def get_cotacao_dolar():
    """
    Consulta a API Frankfurter para obter a cotação atual do dólar em BRL
    """
    try:
        api_url = f"{current_app.config['FRANKFURTER_API_URL']}/cotacao"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao consultar Frankfurter: {str(e)}")
        return None


def calcular_saldo_usd_usuario(user_id):
    """
    Calcula o saldo em USD para um usuário com base em suas transações
    """
    from .models import Transacao
    
    transacoes = Transacao.query.filter_by(user_id=user_id).all()
    
    saldo_usd = 0
    
    for transacao in transacoes:
        if transacao.tipo == 'compra':
            saldo_usd += transacao.quantidade_usd
        else:  # venda
            saldo_usd -= transacao.quantidade_usd
    
    return saldo_usd