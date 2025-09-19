"""Initialize a aplicação Flask e configure extensões necessárias."""

from contextlib import suppress

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import config

# Inicializa extensões Flask sem vincular a uma aplicação específica
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()
api = Flask(__name__)


def create_app(config_name="default"):
    """Crie e configure uma instância da aplicação Flask usando padrão Factory.

    Args:
        config_name (str): Nome da configuração a ser utilizada

    Returns:
        Flask: Instância configurada da aplicação Flask
    """
    # Cria instância da aplicação Flask

    # Carrega configuração baseada no ambiente especificado
    global api
    api.config.from_object(config[config_name])

    # Inicializa extensões com a aplicação
    db.init_app(api)
    migrate.init_app(api, db)
    cors.init_app(api, origins=api.config["CORS_ORIGINS"])
    jwt.init_app(api)
    init_database(app=api)
    # Registra blueprints das rotas da aplicação
    from api.routes.advogados import advogados_bp
    from api.routes.auth import auth_bp
    from api.routes.clientes import clientes_bp
    from api.routes.dashboard import dashboard_bp
    from api.routes.main import main_bp
    from api.routes.processos import processos_bp

    api.register_blueprint(main_bp)
    api.register_blueprint(auth_bp, url_prefix="/api/auth")
    api.register_blueprint(processos_bp, url_prefix="/api/processos")
    api.register_blueprint(clientes_bp, url_prefix="/api/clientes")
    api.register_blueprint(advogados_bp, url_prefix="/api/advogados")
    api.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    # Registra manipuladores de erro personalizados

    with api.app_context():
        import api.routes

        return api


def init_database(app: Flask) -> None:
    with app.app_context():
        from api.models.usuario import Usuario

        db.create_all()

        with suppress(Exception):
            usuario = Usuario(
                nome="Teste Login",
                email="login@teste.com",
                tipo_usuario="usuario",
                ativo=True,
            )
            usuario.set_password("senha123")
            usuario.save()
