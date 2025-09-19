"""Defina rotas de autenticação para login e gerenciamento de usuários."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models.usuario import Usuario

# Cria blueprint para rotas de autenticação
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Execute login do usuário e retorne token de acesso JWT."""
    try:
        # Obtém dados do request JSON
        data = request.get_json()

        if not data or not data.get("email") or not data.get("senha"):
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400

        # Busca usuário pelo email
        usuario = db.session.query(Usuario).filter_by(email=data["email"]).first()

        if not usuario or not usuario.check_password(data["senha"]):
            return jsonify({"erro": "Credenciais inválidas"}), 401

        if not usuario.ativo:
            return jsonify({"erro": "Usuário inativo"}), 401

        # Gera token de acesso
        token = usuario.generate_token()

        return jsonify(
            {
                "token": token,
                "usuario": {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "email": usuario.email,
                    "tipo_usuario": usuario.tipo_usuario,
                },
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@auth_bp.route("/registro", methods=["POST"])
def registro():
    """Registre um novo usuário no sistema."""
    try:
        # Obtém dados do request JSON
        data = request.get_json()

        # Validação de campos obrigatórios
        campos_obrigatorios = ["nome", "email", "senha"]
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({"erro": f"Campo {campo} é obrigatório"}), 400

        # Verifica se email já existe
        if Usuario.query.filter_by(email=data["email"]).first():
            return jsonify({"erro": "Email já cadastrado"}), 409

        # Cria novo usuário
        usuario = Usuario(
            nome=data["nome"],
            email=data["email"],
            tipo_usuario=data.get("tipo_usuario", "usuario"),
        )
        usuario.set_password(data["senha"])

        # Salva no banco de dados
        usuario.save()

        return jsonify(
            {
                "mensagem": "Usuário criado com sucesso",
                "usuario": {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "email": usuario.email,
                    "tipo_usuario": usuario.tipo_usuario,
                },
            }
        ), 201

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@auth_bp.route("/perfil", methods=["GET"])
@jwt_required()
def perfil():
    """Retorne informações do perfil do usuário autenticado."""
    try:
        # Obtém ID do usuário a partir do token
        usuario_id = get_jwt_identity()

        # Busca usuário no banco de dados
        usuario = db.session.get(Usuario, usuario_id)

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        return jsonify(
            {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "tipo_usuario": usuario.tipo_usuario,
                "ativo": usuario.ativo,
                "created_at": usuario.created_at.isoformat(),
                "updated_at": usuario.updated_at.isoformat(),
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@auth_bp.route("/perfil", methods=["PUT"])
@jwt_required()
def atualizar_perfil():
    """Atualize informações do perfil do usuário autenticado."""
    try:
        # Obtém ID do usuário a partir do token
        usuario_id = get_jwt_identity()

        # Busca usuário no banco de dados
        usuario = db.session.get(Usuario, usuario_id)

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        # Obtém dados do request
        data = request.get_json()

        # Atualiza campos permitidos
        if "nome" in data:
            usuario.nome = data["nome"]

        if "senha" in data and data["senha"]:
            usuario.set_password(data["senha"])

        # Salva alterações
        db.session.commit()

        return jsonify(
            {
                "mensagem": "Perfil atualizado com sucesso",
                "usuario": {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "email": usuario.email,
                    "tipo_usuario": usuario.tipo_usuario,
                },
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500
