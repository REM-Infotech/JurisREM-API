"""Defina o modelo Usuario para autenticação e controle de acesso."""

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models._base import BaseModel


class Usuario(BaseModel):
    """Represente um usuário do sistema com capacidades de autenticação."""

    __tablename__ = "usuarios"

    # Informações básicas do usuário
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo: bool = db.Column(db.Boolean, default=True, nullable=False)

    # Tipo de usuário (admin, advogado, secretario, etc.)
    tipo_usuario = db.Column(db.String(50), default="usuario", nullable=False)

    def set_password(self, senha):
        """Defina a senha do usuário usando hash seguro."""
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        """Verifique se a senha fornecida corresponde ao hash armazenado.

        Args:
            senha (str): Senha em texto plano para verificação

        Returns:
            bool: True se a senha estiver correta, False caso contrário
        """
        return check_password_hash(self.senha_hash, senha)

    def generate_token(self):
        """Gere um token JWT para autenticação do usuário.

        Returns:
            str: Token JWT válido para o usuário
        """
        # Inclui informações básicas do usuário no token
        additional_claims = {"tipo_usuario": self.tipo_usuario, "nome": self.nome}
        return create_access_token(
            identity=self.id, additional_claims=additional_claims
        )

    def __repr__(self):
        """Retorne representação string do objeto Usuario."""
        return f"<Usuario {self.email}>"
