"""Defina rotas para gerenciamento de clientes jurídicos."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from app import db
from app.models.cliente import Cliente

# Cria blueprint para rotas de clientes
clientes_bp = Blueprint("clientes", __name__)


@clientes_bp.route("/", methods=["GET"])
@jwt_required()
def listar_clientes():
    """Liste todos os clientes com opção de busca e paginação."""
    try:
        # Parâmetros de consulta
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", "")
        ativo_only = request.args.get("ativo", "true").lower() == "true"

        # Monta query base
        query = Cliente.query

        # Filtro por status ativo
        if ativo_only:
            query = query.filter(Cliente.ativo == True)  # noqa: E712

        # Filtro de busca por nome, CPF/CNPJ ou email
        if search:
            search_filter = or_(
                Cliente.nome.ilike(f"%{search}%"),
                Cliente.cpf_cnpj.ilike(f"%{search}%"),
                Cliente.email.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Ordena por nome
        query = query.order_by(Cliente.nome)

        # Executa paginação
        clientes_paginados = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Monta resposta
        clientes_data = []
        for cliente in clientes_paginados.items:
            clientes_data.append(
                {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "cpf_cnpj": cliente.cpf_cnpj,
                    "email": cliente.email,
                    "telefone": cliente.telefone,
                    "tipo_pessoa": cliente.tipo_pessoa,
                    "ativo": cliente.ativo,
                    "total_processos": len(cliente.processos),
                }
            )

        return jsonify(
            {
                "clientes": clientes_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": clientes_paginados.total,
                    "pages": clientes_paginados.pages,
                    "has_next": clientes_paginados.has_next,
                    "has_prev": clientes_paginados.has_prev,
                },
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@clientes_bp.route("/", methods=["POST"])
@jwt_required()
def criar_cliente():
    """Crie um novo cliente no sistema."""
    try:
        # Obtém dados do request
        data = request.get_json()

        # Validação de campos obrigatórios
        campos_obrigatorios = ["nome", "cpf_cnpj", "tipo_pessoa"]
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({"erro": f"Campo {campo} é obrigatório"}), 400

        # Verifica se CPF/CNPJ já existe
        if Cliente.query.filter_by(cpf_cnpj=data["cpf_cnpj"]).first():
            return jsonify({"erro": "CPF/CNPJ já cadastrado"}), 409

        # Cria novo cliente
        cliente = Cliente(
            nome=data["nome"],
            cpf_cnpj=data["cpf_cnpj"],
            tipo_pessoa=data["tipo_pessoa"],
            email=data.get("email"),
            telefone=data.get("telefone"),
            endereco_rua=data.get("endereco_rua"),
            endereco_numero=data.get("endereco_numero"),
            endereco_complemento=data.get("endereco_complemento"),
            endereco_bairro=data.get("endereco_bairro"),
            endereco_cidade=data.get("endereco_cidade"),
            endereco_estado=data.get("endereco_estado"),
            endereco_cep=data.get("endereco_cep"),
            profissao=data.get("profissao"),
            estado_civil=data.get("estado_civil"),
            observacoes=data.get("observacoes"),
        )

        # Salva no banco de dados
        cliente.save()

        return jsonify(
            {
                "mensagem": "Cliente criado com sucesso",
                "cliente": {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "cpf_cnpj": cliente.cpf_cnpj,
                    "email": cliente.email,
                    "tipo_pessoa": cliente.tipo_pessoa,
                },
            }
        ), 201

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@clientes_bp.route("/<int:cliente_id>", methods=["GET"])
@jwt_required()
def obter_cliente(cliente_id):
    """Obtenha detalhes completos de um cliente específico."""
    try:
        # Busca cliente pelo ID
        cliente = Cliente.query.get(cliente_id)

        if not cliente:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        # Retorna dados completos do cliente
        return jsonify(
            {
                "id": cliente.id,
                "nome": cliente.nome,
                "cpf_cnpj": cliente.cpf_cnpj,
                "email": cliente.email,
                "telefone": cliente.telefone,
                "tipo_pessoa": cliente.tipo_pessoa,
                "endereco_rua": cliente.endereco_rua,
                "endereco_numero": cliente.endereco_numero,
                "endereco_complemento": cliente.endereco_complemento,
                "endereco_bairro": cliente.endereco_bairro,
                "endereco_cidade": cliente.endereco_cidade,
                "endereco_estado": cliente.endereco_estado,
                "endereco_cep": cliente.endereco_cep,
                "endereco_completo": cliente.endereco_completo,
                "profissao": cliente.profissao,
                "estado_civil": cliente.estado_civil,
                "observacoes": cliente.observacoes,
                "ativo": cliente.ativo,
                "created_at": cliente.created_at.isoformat(),
                "updated_at": cliente.updated_at.isoformat(),
                "total_processos": len(cliente.processos),
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@clientes_bp.route("/<int:cliente_id>", methods=["PUT"])
@jwt_required()
def atualizar_cliente(cliente_id):
    """Atualize informações de um cliente existente."""
    try:
        # Busca cliente pelo ID
        cliente = Cliente.query.get(cliente_id)

        if not cliente:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        # Obtém dados do request
        data = request.get_json()

        # Verifica se CPF/CNPJ já existe em outro cliente
        if "cpf_cnpj" in data and data["cpf_cnpj"] != cliente.cpf_cnpj:
            if Cliente.query.filter_by(cpf_cnpj=data["cpf_cnpj"]).first():
                return jsonify({"erro": "CPF/CNPJ já cadastrado"}), 409

        # Atualiza campos permitidos
        campos_atualizaveis = [
            "nome",
            "cpf_cnpj",
            "email",
            "telefone",
            "tipo_pessoa",
            "endereco_rua",
            "endereco_numero",
            "endereco_complemento",
            "endereco_bairro",
            "endereco_cidade",
            "endereco_estado",
            "endereco_cep",
            "profissao",
            "estado_civil",
            "observacoes",
            "ativo",
        ]

        for campo in campos_atualizaveis:
            if campo in data:
                setattr(cliente, campo, data[campo])

        # Salva alterações
        db.session.commit()

        return jsonify(
            {
                "mensagem": "Cliente atualizado com sucesso",
                "cliente": {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "cpf_cnpj": cliente.cpf_cnpj,
                    "email": cliente.email,
                    "tipo_pessoa": cliente.tipo_pessoa,
                },
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@clientes_bp.route("/<int:cliente_id>", methods=["DELETE"])
@jwt_required()
def excluir_cliente(cliente_id):
    """Exclua um cliente do sistema (soft delete)."""
    try:
        # Busca cliente pelo ID
        cliente = Cliente.query.get(cliente_id)

        if not cliente:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        # Verifica se cliente tem processos ativos
        if cliente.processos:
            return jsonify(
                {"erro": "Não é possível excluir cliente com processos associados"}
            ), 400

        # Realiza soft delete (marca como inativo)
        cliente.ativo = False
        db.session.commit()

        return jsonify({"mensagem": "Cliente excluído com sucesso"}), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500
