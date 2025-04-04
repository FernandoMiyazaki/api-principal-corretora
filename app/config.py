import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = False
    VIACEP_API_URL = os.environ.get('VIACEP_API_URL', 'http://api-secundaria-viacep:5001')
    FRANKFURTER_API_URL = os.environ.get('FRANKFURTER_API_URL', 'http://api-secundaria-frankfurter:5002')


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 'postgresql://postgres:postgres@db:5432/api_principal_test'
    )


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}