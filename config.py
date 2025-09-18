"""Configure a aplicação Flask para diferentes ambientes de execução."""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class Config:
    """Classe base de configuração contendo configurações comuns a todos os ambientes."""
    
    # Configurações básicas da aplicação Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuração JWT para autenticação de usuários
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = False  # Token não expira por padrão
    
    # Configuração CORS para permitir requisições de diferentes origens
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']


class DevelopmentConfig(Config):
    """Configure a aplicação para o ambiente de desenvolvimento."""
    
    DEBUG = True  # Habilita modo debug para desenvolvimento
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///jurisrem_dev.db'


class ProductionConfig(Config):
    """Configure a aplicação para o ambiente de produção."""
    
    DEBUG = False  # Desabilita modo debug em produção
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///jurisrem.db'


class TestingConfig(Config):
    """Configure a aplicação para execução de testes automatizados."""
    
    TESTING = True  # Habilita modo de teste
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Banco de dados em memória para testes


# Dicionário para mapear nomes de ambiente para classes de configuração
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}