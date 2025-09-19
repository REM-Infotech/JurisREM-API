"""Defina rotas para gerenciamento de processos jurídicos."""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_

from api import db
from api.models.advogado import Advogado
from api.models.cliente import Cliente
from api.models.processo import Andamento, Processo

# Cria blueprint para rotas de processos
processos_bp = Blueprint("processos", __name__)


@processos_bp.route("/", methods=["GET", "POST", "OPTIONS"])
@jwt_required()
def listar_processos():
    """Liste todos os processos com opção de filtros e paginação."""
    try:
        # Parâmetros de consulta
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", "")
        status = request.args.get("status", "")
        area_juridica = request.args.get("area_juridica", "")
        advogado_id = request.args.get("advogado_id", type=int)
        cliente_id = request.args.get("cliente_id", type=int)
        prioridade = request.args.get("prioridade", "")

        # Monta query base com joins para otimizar consultas
        query = Processo.query.join(Cliente).join(Advogado)

        # Filtro de busca por número, título ou nome do cliente
        if search:
            search_filter = or_(
                Processo.numero_processo.ilike(f"%{search}%"),
                Processo.titulo.ilike(f"%{search}%"),
                Cliente.nome.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Filtros específicos
        if status:
            query = query.filter(Processo.status == status)

        if area_juridica:
            query = query.filter(Processo.area_juridica == area_juridica)

        if advogado_id:
            query = query.filter(Processo.advogado_id == advogado_id)

        if cliente_id:
            query = query.filter(Processo.cliente_id == cliente_id)

        if prioridade:
            query = query.filter(Processo.prioridade == prioridade)

        # Ordena por data de criação (mais recentes primeiro)
        query = query.order_by(Processo.created_at.desc())

        # Executa paginação
        processos_paginados = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Monta resposta
        processos_data = []
        for processo in processos_paginados.items:
            processos_data.append(
                {
                    "id": processo.id,
                    "numero_processo": processo.numero_processo,
                    "numero_formatado": processo.numero_formatado,
                    "numero_interno": processo.numero_interno,
                    "titulo": processo.titulo,
                    "area_juridica": processo.area_juridica,
                    "status": processo.status,
                    "status_descricao": processo.status_descricao,
                    "prioridade": processo.prioridade,
                    "prioridade_descricao": processo.prioridade_descricao,
                    "data_distribuicao": processo.data_distribuicao.isoformat()
                    if processo.data_distribuicao
                    else None,
                    "valor_causa": float(processo.valor_causa)
                    if processo.valor_causa
                    else None,
                    "cliente": {
                        "id": processo.cliente.id,
                        "nome": processo.cliente.nome,
                        "cpf_cnpj": processo.cliente.cpf_cnpj,
                    },
                    "advogado": {
                        "id": processo.advogado_responsavel.id,
                        "nome": processo.advogado_responsavel.nome,
                        "oab_completa": processo.advogado_responsavel.oab_completa,
                    },
                    "total_andamentos": len(processo.andamentos),
                    "created_at": processo.created_at.isoformat(),
                }
            )

        return jsonify(
            {
                "processos": processos_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": processos_paginados.total,
                    "pages": processos_paginados.pages,
                    "has_next": processos_paginados.has_next,
                    "has_prev": processos_paginados.has_prev,
                },
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@processos_bp.route("/", methods=["POST"])
@jwt_required()
def criar_processo():
    """Crie um novo processo jurídico no sistema."""
    try:
        # Obtém dados do request
        data = request.get_json()

        # Validação de campos obrigatórios
        campos_obrigatorios = [
            "numero_processo",
            "titulo",
            "area_juridica",
            "cliente_id",
            "advogado_id",
        ]
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({"erro": f"Campo {campo} é obrigatório"}), 400

        # Verifica se número do processo já existe
        if Processo.query.filter_by(numero_processo=data["numero_processo"]).first():
            return jsonify({"erro": "Número do processo já cadastrado"}), 409

        # Verifica se cliente existe
        cliente = Cliente.query.get(data["cliente_id"])
        if not cliente:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        # Verifica se advogado existe
        advogado = Advogado.query.get(data["advogado_id"])
        if not advogado:
            return jsonify({"erro": "Advogado não encontrado"}), 404

        # Cria novo processo
        processo = Processo(
            numero_processo=data["numero_processo"],
            numero_interno=data.get("numero_interno"),
            titulo=data["titulo"],
            descricao=data.get("descricao"),
            area_juridica=data["area_juridica"],
            tipo_acao=data.get("tipo_acao"),
            status=data.get("status", "em_andamento"),
            data_distribuicao=datetime.fromisoformat(data["data_distribuicao"])
            if data.get("data_distribuicao")
            else None,
            tribunal=data.get("tribunal"),
            vara=data.get("vara"),
            juiz=data.get("juiz"),
            valor_causa=data.get("valor_causa"),
            valor_honorarios=data.get("valor_honorarios"),
            forma_pagamento=data.get("forma_pagamento"),
            prioridade=data.get("prioridade", "normal"),
            observacoes=data.get("observacoes"),
            observacoes_internas=data.get("observacoes_internas"),
            cliente_id=data["cliente_id"],
            advogado_id=data["advogado_id"],
        )

        # Salva no banco de dados
        processo.save()

        # Cria andamento inicial se fornecido
        if data.get("andamento_inicial"):
            andamento = Andamento(
                data_andamento=datetime.utcnow(),
                tipo_andamento="Abertura do Processo",
                descricao=data["andamento_inicial"],
                processo_id=processo.id,
                usuario_id=get_jwt_identity(),
            )
            andamento.save()

        return jsonify(
            {
                "mensagem": "Processo criado com sucesso",
                "processo": {
                    "id": processo.id,
                    "numero_processo": processo.numero_processo,
                    "titulo": processo.titulo,
                    "status": processo.status,
                },
            }
        ), 201

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@processos_bp.route("/<int:processo_id>", methods=["GET"])
@jwt_required()
def obter_processo(processo_id):
    """Obtenha detalhes completos de um processo específico."""
    try:
        # Busca processo pelo ID com relacionamentos
        processo = Processo.query.options(
            db.joinedload(Processo.cliente),
            db.joinedload(Processo.advogado_responsavel),
            db.joinedload(Processo.andamentos).joinedload(Andamento.usuario),
        ).get(processo_id)

        if not processo:
            return jsonify({"erro": "Processo não encontrado"}), 404

        # Monta lista de andamentos
        andamentos_data = []
        for andamento in processo.andamentos:
            andamentos_data.append(
                {
                    "id": andamento.id,
                    "data_andamento": andamento.data_andamento.isoformat(),
                    "tipo_andamento": andamento.tipo_andamento,
                    "descricao": andamento.descricao,
                    "observacoes": andamento.observacoes,
                    "documento_anexo": andamento.documento_anexo,
                    "usuario": {
                        "id": andamento.usuario.id,
                        "nome": andamento.usuario.nome,
                    }
                    if andamento.usuario
                    else None,
                    "created_at": andamento.created_at.isoformat(),
                }
            )

        # Retorna dados completos do processo
        return jsonify(
            {
                "id": processo.id,
                "numero_processo": processo.numero_processo,
                "numero_formatado": processo.numero_formatado,
                "numero_interno": processo.numero_interno,
                "titulo": processo.titulo,
                "descricao": processo.descricao,
                "area_juridica": processo.area_juridica,
                "tipo_acao": processo.tipo_acao,
                "status": processo.status,
                "status_descricao": processo.status_descricao,
                "data_distribuicao": processo.data_distribuicao.isoformat()
                if processo.data_distribuicao
                else None,
                "data_conclusao": processo.data_conclusao.isoformat()
                if processo.data_conclusao
                else None,
                "tribunal": processo.tribunal,
                "vara": processo.vara,
                "juiz": processo.juiz,
                "valor_causa": float(processo.valor_causa)
                if processo.valor_causa
                else None,
                "valor_honorarios": float(processo.valor_honorarios)
                if processo.valor_honorarios
                else None,
                "forma_pagamento": processo.forma_pagamento,
                "prioridade": processo.prioridade,
                "prioridade_descricao": processo.prioridade_descricao,
                "observacoes": processo.observacoes,
                "observacoes_internas": processo.observacoes_internas,
                "cliente": {
                    "id": processo.cliente.id,
                    "nome": processo.cliente.nome,
                    "cpf_cnpj": processo.cliente.cpf_cnpj,
                    "email": processo.cliente.email,
                    "telefone": processo.cliente.telefone,
                },
                "advogado": {
                    "id": processo.advogado_responsavel.id,
                    "nome": processo.advogado_responsavel.nome,
                    "oab_completa": processo.advogado_responsavel.oab_completa,
                    "email": processo.advogado_responsavel.email,
                },
                "andamentos": andamentos_data,
                "created_at": processo.created_at.isoformat(),
                "updated_at": processo.updated_at.isoformat(),
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@processos_bp.route("/<int:processo_id>", methods=["PUT"])
@jwt_required()
def atualizar_processo(processo_id):
    """Atualize informações de um processo existente."""
    try:
        # Busca processo pelo ID
        processo = Processo.query.get(processo_id)

        if not processo:
            return jsonify({"erro": "Processo não encontrado"}), 404

        # Obtém dados do request
        data = request.get_json()

        # Verifica se número do processo já existe em outro processo
        if (
            "numero_processo" in data
            and data["numero_processo"] != processo.numero_processo
        ):
            if Processo.query.filter_by(
                numero_processo=data["numero_processo"]
            ).first():
                return jsonify({"erro": "Número do processo já cadastrado"}), 409

        # Valida IDs de relacionamentos se alterados
        if "cliente_id" in data and data["cliente_id"] != processo.cliente_id:
            if not Cliente.query.get(data["cliente_id"]):
                return jsonify({"erro": "Cliente não encontrado"}), 404

        if "advogado_id" in data and data["advogado_id"] != processo.advogado_id:
            if not Advogado.query.get(data["advogado_id"]):
                return jsonify({"erro": "Advogado não encontrado"}), 404

        # Atualiza campos permitidos
        campos_atualizaveis = [
            "numero_processo",
            "numero_interno",
            "titulo",
            "descricao",
            "area_juridica",
            "tipo_acao",
            "status",
            "tribunal",
            "vara",
            "juiz",
            "valor_causa",
            "valor_honorarios",
            "forma_pagamento",
            "prioridade",
            "observacoes",
            "observacoes_internas",
            "cliente_id",
            "advogado_id",
        ]

        for campo in campos_atualizaveis:
            if campo in data:
                setattr(processo, campo, data[campo])

        # Atualiza datas especiais
        if "data_distribuicao" in data:
            processo.data_distribuicao = (
                datetime.fromisoformat(data["data_distribuicao"])
                if data["data_distribuicao"]
                else None
            )

        if "data_conclusao" in data:
            processo.data_conclusao = (
                datetime.fromisoformat(data["data_conclusao"])
                if data["data_conclusao"]
                else None
            )

        # Salva alterações
        db.session.commit()

        return jsonify(
            {
                "mensagem": "Processo atualizado com sucesso",
                "processo": {
                    "id": processo.id,
                    "numero_processo": processo.numero_processo,
                    "titulo": processo.titulo,
                    "status": processo.status,
                },
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@processos_bp.route("/<int:processo_id>/andamentos", methods=["GET"])
@jwt_required()
def listar_andamentos(processo_id):
    """Liste todos os andamentos de um processo específico."""
    try:
        # Verifica se processo existe
        processo = Processo.query.get(processo_id)
        if not processo:
            return jsonify({"erro": "Processo não encontrado"}), 404

        # Parâmetros de consulta
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Busca andamentos com paginação
        andamentos_query = Andamento.query.filter_by(processo_id=processo_id).order_by(
            Andamento.data_andamento.desc()
        )
        andamentos_paginados = andamentos_query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Monta resposta
        andamentos_data = []
        for andamento in andamentos_paginados.items:
            andamentos_data.append(
                {
                    "id": andamento.id,
                    "data_andamento": andamento.data_andamento.isoformat(),
                    "tipo_andamento": andamento.tipo_andamento,
                    "descricao": andamento.descricao,
                    "observacoes": andamento.observacoes,
                    "documento_anexo": andamento.documento_anexo,
                    "usuario": {
                        "id": andamento.usuario.id,
                        "nome": andamento.usuario.nome,
                    }
                    if andamento.usuario
                    else None,
                    "created_at": andamento.created_at.isoformat(),
                }
            )

        return jsonify(
            {
                "andamentos": andamentos_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": andamentos_paginados.total,
                    "pages": andamentos_paginados.pages,
                    "has_next": andamentos_paginados.has_next,
                    "has_prev": andamentos_paginados.has_prev,
                },
            }
        ), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@processos_bp.route("/<int:processo_id>/andamentos", methods=["POST"])
@jwt_required()
def criar_andamento(processo_id):
    """Crie um novo andamento para um processo específico."""
    try:
        # Verifica se processo existe
        processo = Processo.query.get(processo_id)
        if not processo:
            return jsonify({"erro": "Processo não encontrado"}), 404

        # Obtém dados do request
        data = request.get_json()

        # Validação de campos obrigatórios
        if not data.get("tipo_andamento") or not data.get("descricao"):
            return jsonify(
                {"erro": "Tipo e descrição do andamento são obrigatórios"}
            ), 400

        # Cria novo andamento
        andamento = Andamento(
            data_andamento=datetime.fromisoformat(data["data_andamento"])
            if data.get("data_andamento")
            else datetime.utcnow(),
            tipo_andamento=data["tipo_andamento"],
            descricao=data["descricao"],
            observacoes=data.get("observacoes"),
            documento_anexo=data.get("documento_anexo"),
            processo_id=processo_id,
            usuario_id=get_jwt_identity(),
        )

        # Salva no banco de dados
        andamento.save()

        return jsonify(
            {
                "mensagem": "Andamento criado com sucesso",
                "andamento": {
                    "id": andamento.id,
                    "tipo_andamento": andamento.tipo_andamento,
                    "data_andamento": andamento.data_andamento.isoformat(),
                },
            }
        ), 201

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500
