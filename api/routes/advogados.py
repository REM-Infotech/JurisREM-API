"""Defina rotas para gerenciamento de advogados da equipe jurídica."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from api import db
from api.models.advogado import Advogado

# Cria blueprint para rotas de advogados
advogados_bp = Blueprint("advogados", __name__)


@advogados_bp.route("/", methods=["GET"])
@jwt_required()
def listar_advogados():
    """Liste todos os advogados com opção de busca e paginação."""
    try:
        # Parâmetros de consulta
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", "")
        ativo_only = request.args.get("ativo", "true").lower() == "true"

        # Monta query base
        query = Advogado.query

        # Filtro por status ativo
        if ativo_only:
            query = query.filter(Advogado.ativo == True)  # noqa: E712

        # Filtro de busca por nome, OAB ou email
        if search:
            search_filter = or_(
                Advogado.nome.ilike(f"%{search}%"),
                Advogado.oab_numero.ilike(f"%{search}%"),
                Advogado.email.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Ordena por nome
        query = query.order_by(Advogado.nome)

        # Executa paginação
        advogados_paginados = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Monta resposta
        advogados_data = []
        for advogado in advogados_paginados.items:
            advogados_data.append(
                {
                    "id": advogado.id,
                    "nome": advogado.nome,
                    "oab_numero": advogado.oab_numero,
                    "oab_estado": advogado.oab_estado,
                    "oab_completa": advogado.oab_completa,
                    "email": advogado.email,
                    "telefone": advogado.telefone,
                    "ativo": advogado.ativo,
                    "total_processos": len(advogado.processos),
                    "especialidades": advogado.get_especialidades_list(),
                }
            )

        return jsonify(
            {
                "advogados": advogados_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": advogados_paginados.total,
                    "pages": advogados_paginados.pages,
                    "has_next": advogados_paginados.has_next,
                    "has_prev": advogados_paginados.has_prev,
                },
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@advogados_bp.route("/", methods=["POST"])
@jwt_required()
def criar_advogado():
    """Crie um novo advogado no sistema."""
    try:
        # Obtém dados do request
        data = request.get_json()

        # Validação de campos obrigatórios
        campos_obrigatorios = ["nome", "cpf", "oab_numero", "oab_estado", "email"]
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({"erro": f"Campo {campo} é obrigatório"}), 400

        # Verifica se CPF já existe
        if Advogado.query.filter_by(cpf=data["cpf"]).first():
            return jsonify({"erro": "CPF já cadastrado"}), 409

        # Verifica se OAB já existe
        if Advogado.query.filter_by(
            oab_numero=data["oab_numero"], oab_estado=data["oab_estado"]
        ).first():
            return jsonify({"erro": "Número da OAB já cadastrado"}), 409

        # Verifica se email já existe
        if Advogado.query.filter_by(email=data["email"]).first():
            return jsonify({"erro": "Email já cadastrado"}), 409

        # Cria novo advogado
        advogado = Advogado(
            nome=data["nome"],
            cpf=data["cpf"],
            oab_numero=data["oab_numero"],
            oab_estado=data["oab_estado"],
            email=data["email"],
            telefone=data.get("telefone"),
            data_admissao=data.get("data_admissao"),
            endereco_rua=data.get("endereco_rua"),
            endereco_numero=data.get("endereco_numero"),
            endereco_complemento=data.get("endereco_complemento"),
            endereco_bairro=data.get("endereco_bairro"),
            endereco_cidade=data.get("endereco_cidade"),
            endereco_estado=data.get("endereco_estado"),
            endereco_cep=data.get("endereco_cep"),
            biografia=data.get("biografia"),
            observacoes=data.get("observacoes"),
        )

        # Define especialidades se fornecidas
        if "especialidades" in data:
            advogado.set_especialidades_list(data["especialidades"])

        # Salva no banco de dados
        advogado.save()

        return jsonify(
            {
                "mensagem": "Advogado criado com sucesso",
                "advogado": {
                    "id": advogado.id,
                    "nome": advogado.nome,
                    "oab_completa": advogado.oab_completa,
                    "email": advogado.email,
                },
            }
        ), 201

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@advogados_bp.route("/<int:advogado_id>", methods=["GET"])
@jwt_required()
def obter_advogado(advogado_id):
    """Obtenha detalhes completos de um advogado específico."""
    try:
        # Busca advogado pelo ID
        advogado = Advogado.query.get(advogado_id)

        if not advogado:
            return jsonify({"erro": "Advogado não encontrado"}), 404

        # Retorna dados completos do advogado
        return jsonify(
            {
                "id": advogado.id,
                "nome": advogado.nome,
                "cpf": advogado.cpf,
                "oab_numero": advogado.oab_numero,
                "oab_estado": advogado.oab_estado,
                "oab_completa": advogado.oab_completa,
                "email": advogado.email,
                "telefone": advogado.telefone,
                "data_admissao": advogado.data_admissao.isoformat()
                if advogado.data_admissao
                else None,
                "data_demissao": advogado.data_demissao.isoformat()
                if advogado.data_demissao
                else None,
                "endereco_rua": advogado.endereco_rua,
                "endereco_numero": advogado.endereco_numero,
                "endereco_complemento": advogado.endereco_complemento,
                "endereco_bairro": advogado.endereco_bairro,
                "endereco_cidade": advogado.endereco_cidade,
                "endereco_estado": advogado.endereco_estado,
                "endereco_cep": advogado.endereco_cep,
                "endereco_completo": advogado.endereco_completo,
                "biografia": advogado.biografia,
                "observacoes": advogado.observacoes,
                "especialidades": advogado.get_especialidades_list(),
                "ativo": advogado.ativo,
                "created_at": advogado.created_at.isoformat(),
                "updated_at": advogado.updated_at.isoformat(),
                "total_processos": len(advogado.processos),
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@advogados_bp.route("/<int:advogado_id>", methods=["PUT"])
@jwt_required()
def atualizar_advogado(advogado_id):
    """Atualize informações de um advogado existente."""
    try:
        # Busca advogado pelo ID
        advogado = Advogado.query.get(advogado_id)

        if not advogado:
            return jsonify({"erro": "Advogado não encontrado"}), 404

        # Obtém dados do request
        data = request.get_json()

        # Verifica unicidade de campos se alterados
        if "cpf" in data and data["cpf"] != advogado.cpf:
            if Advogado.query.filter_by(cpf=data["cpf"]).first():
                return jsonify({"erro": "CPF já cadastrado"}), 409

        if "email" in data and data["email"] != advogado.email:
            if Advogado.query.filter_by(email=data["email"]).first():
                return jsonify({"erro": "Email já cadastrado"}), 409

        if (
            "oab_numero" in data
            and "oab_estado" in data
            and (
                data["oab_numero"] != advogado.oab_numero
                or data["oab_estado"] != advogado.oab_estado
            )
        ):
            if Advogado.query.filter_by(
                oab_numero=data["oab_numero"], oab_estado=data["oab_estado"]
            ).first():
                return jsonify({"erro": "Número da OAB já cadastrado"}), 409

        # Atualiza campos permitidos
        campos_atualizaveis = [
            "nome",
            "cpf",
            "oab_numero",
            "oab_estado",
            "email",
            "telefone",
            "data_admissao",
            "data_demissao",
            "endereco_rua",
            "endereco_numero",
            "endereco_complemento",
            "endereco_bairro",
            "endereco_cidade",
            "endereco_estado",
            "endereco_cep",
            "biografia",
            "observacoes",
            "ativo",
        ]

        for campo in campos_atualizaveis:
            if campo in data:
                setattr(advogado, campo, data[campo])

        # Atualiza especialidades se fornecidas
        if "especialidades" in data:
            advogado.set_especialidades_list(data["especialidades"])

        # Salva alterações
        db.session.commit()

        return jsonify(
            {
                "mensagem": "Advogado atualizado com sucesso",
                "advogado": {
                    "id": advogado.id,
                    "nome": advogado.nome,
                    "oab_completa": advogado.oab_completa,
                    "email": advogado.email,
                },
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@advogados_bp.route("/<int:advogado_id>", methods=["DELETE"])
@jwt_required()
def excluir_advogado(advogado_id):
    """Exclua um advogado do sistema (soft delete)."""
    try:
        # Busca advogado pelo ID
        advogado = Advogado.query.get(advogado_id)

        if not advogado:
            return jsonify({"erro": "Advogado não encontrado"}), 404

        # Verifica se advogado tem processos ativos
        if advogado.processos:
            return jsonify(
                {"erro": "Não é possível excluir advogado com processos associados"}
            ), 400

        # Realiza soft delete (marca como inativo)
        advogado.ativo = False
        db.session.commit()

        return jsonify({"mensagem": "Advogado excluído com sucesso"}), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500
