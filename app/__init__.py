"""Initialize a aplicação Flask e configure extensões necessárias."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config

# Inicializa extensões Flask sem vincular a uma aplicação específica
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()


def create_app(config_name='default'):
    """Crie e configure uma instância da aplicação Flask usando padrão Factory.
    
    Args:
        config_name (str): Nome da configuração a ser utilizada
    
    Returns:
        Flask: Instância configurada da aplicação Flask
    """
    # Cria instância da aplicação Flask
    app = Flask(__name__)
    
    # Carrega configuração baseada no ambiente especificado
    app.config.from_object(config[config_name])
    
    # Inicializa extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    jwt.init_app(app)
    
    # Registra blueprints das rotas da aplicação
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.processos import processos_bp
    from app.routes.clientes import clientes_bp
    from app.routes.advogados import advogados_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(processos_bp, url_prefix='/api/processos')
    app.register_blueprint(clientes_bp, url_prefix='/api/clientes')
    app.register_blueprint(advogados_bp, url_prefix='/api/advogados')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Registra manipuladores de erro personalizados
    from app.routes.errors import register_error_handlers
    register_error_handlers(app)
    
    return app