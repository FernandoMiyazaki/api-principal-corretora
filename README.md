# Sistema de Câmbio com Flask/Python

Este projeto consiste em um sistema de APIs REST desenvolvido com Flask/Python, composto por:

1. API Principal: Interface com o usuário, gerenciando usuários e transações de câmbio.
2. API ViaCEP: Consulta de endereços via CEP.
3. API Frankfurter: Consulta de cotações de moedas.

O sistema está containerizado com Docker e utiliza PostgreSQL como banco de dados.

## Estrutura do Projeto

```
sistema-cambio/
├── api-principal-corretora/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── utils.py
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── init-db.sh
│   ├── requirements.txt
│   └── run.py
├── api-secundaria-viacep/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── utils.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
└── api-secundaria-frankfurter/
    ├── app/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── extensions.py
    │   ├── models.py
    │   ├── routes.py
    │   └── utils.py
    ├── Dockerfile
    ├── requirements.txt
    └── run.py
```

## Pré-requisitos

- Docker
- Docker Compose

## Configuração e Execução

### 1. Clone os Repositórios

Crie uma pasta para o projeto e clone os repositórios:

```bash
mkdir sistema-cambio
cd sistema-cambio

# Clone os repositórios (substitua pelos seus repositórios reais)
git clone [URL-DO-REPOSITORIO] api-principal-corretora
git clone [URL-DO-REPOSITORIO] api-secundaria-viacep
git clone [URL-DO-REPOSITORIO] api-secundaria-frankfurter
```

### 2. Configuração dos Ambientes

Certifique-se de que os arquivos `.env` estão presentes em cada diretório:

- `api-principal-corretora/.env`
- `api-secundaria-viacep/.env`
- `api-secundaria-frankfurter/.env`

### 3. Permissão para o Script do Banco de Dados

```bash
cd api-principal-corretora
icacls init-db.sh /grant Everyone:F
```

### 4. Iniciar os Serviços

```bash
docker-compose up -d
```

Este comando irá:
1. Construir as imagens Docker para as três APIs
2. Iniciar o PostgreSQL e configurar os bancos de dados
3. Iniciar o pgAdmin
4. Iniciar as três APIs

### 5. Verificar os Serviços

Após alguns segundos, todos os serviços devem estar em execução:

- API Principal: http://localhost:5000/swagger
- API ViaCEP: http://localhost:5001/swagger
- API Frankfurter: http://localhost:5002/swagger
- pgAdmin: http://localhost:8080

### 6. Acessar o pgAdmin

1. Acesse http://localhost:8080
2. Faça login com:
   - Email: admin@example.com
   - Senha: admin
3. Adicione um novo servidor:
   - Nome: LocalDB
   - Host: db
   - Porta: 5432
   - Usuário: postgres
   - Senha: postgres

## Endpoints da API

### API Principal

- `GET /users`: Lista todos os usuários
- `POST /users`: Cria um novo usuário
- `GET /users/<id>`: Obtém um usuário específico
- `PUT /users/<id>`: Atualiza um usuário
- `DELETE /users/<id>`: Remove um usuário
- `GET /users/<id>/saldo`: Obtém o saldo de um usuário
- `POST /transactions/compra`: Registra uma compra de dólares
- `POST /transactions/venda`: Registra uma venda de dólares
- `GET /transactions/<id>`: Obtém uma transação específica

### API ViaCEP

- `GET /cep/<cep>`: Consulta um CEP
- `POST /cep`: Consulta um CEP via POST
- `GET /cep`: Lista todas as consultas de CEP
- `PUT /cep/<id>`: Atualiza uma consulta de CEP
- `DELETE /cep/<id>`: Remove uma consulta de CEP

### API Frankfurter

- `GET /cotacao`: Obtém a cotação atual do dólar
- `POST /cotacao/converter`: Converte um valor entre moedas
- `GET /cotacao/historico`: Obtém o histórico de cotações

## Desenvolvimento Local

Para desenvolvimento local, você pode usar um ambiente virtual Python:

```bash
# API Principal
cd api-principal-corretora
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py

# API ViaCEP (em outro terminal)
cd api-secundaria-viacep
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py

# API Frankfurter (em outro terminal)
cd api-secundaria-frankfurter
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Parar os Serviços

```bash
cd api-principal-corretora
docker-compose down
```

Para remover volumes e imagens:

```bash
docker-compose down -v --rmi all
```