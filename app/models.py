# Estes modelos não são usados para persistência, apenas para documentação
class User:
    """
    Modelo para documentação de usuário
    """
    id = None
    nome_completo = None
    email = None
    senha = None
    cpf = None
    cep = None
    logradouro = None
    complemento = None
    bairro = None
    localidade = None
    estado = None
    created_at = None
    updated_at = None


class Transacao:
    """
    Modelo para documentação de transação
    """
    id = None
    user_id = None
    tipo = None
    quantidade_usd = None
    valor_brl = None
    cotacao = None
    data_transacao = None