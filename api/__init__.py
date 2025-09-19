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
app = Flask(__name__)


def create_app(config_name="default"):
    """Crie e configure uma instância da aplicação Flask usando padrão Factory.

    Args:
        config_name (str): Nome da configuração a ser utilizada

    Returns:
        Flask: Instância configurada da aplicação Flask
    """
    # Cria instância da aplicação Flask

    # Carrega configuração baseada no ambiente especificado
    global app
    app.config.from_object(config[config_name])

    # Inicializa extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])
    jwt.init_app(app)
    init_database(app=app)
    # Registra blueprints das rotas da aplicação
    from api.routes.advogados import advogados_bp
    from api.routes.auth import auth_bp
    from api.routes.clientes import clientes_bp
    from api.routes.dashboard import dashboard_bp
    from api.routes.main import main_bp
    from api.routes.processos import processos_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(processos_bp, url_prefix="/api/processos")
    app.register_blueprint(clientes_bp, url_prefix="/api/clientes")
    app.register_blueprint(advogados_bp, url_prefix="/api/advogados")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    # Registra manipuladores de erro personalizados

    with app.app_context():
        import api.routes  # noqa: F401

    return app


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
