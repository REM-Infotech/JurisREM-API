"""Defina rotas para dashboard e relatórios administrativos."""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from api.services import DashboardService, RelatorioService

# Cria blueprint para rotas de dashboard
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/estatisticas", methods=["GET"])
@jwt_required()
def obter_estatisticas():
    """Obtenha estatísticas gerais do sistema para dashboard."""
    try:
        # Utiliza serviço para obter estatísticas
        estatisticas = DashboardService.get_estatisticas_gerais()

        return jsonify(estatisticas), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@dashboard_bp.route("/processos-recentes", methods=["GET"])
@jwt_required()
def obter_processos_recentes():
    """Obtenha lista dos processos mais recentes."""
    try:
        # Parâmetro opcional para limite de resultados
        limite = request.args.get("limite", 10, type=int)

        # Utiliza serviço para obter processos recentes
        processos = DashboardService.get_processos_recentes(limite)

        return jsonify({"processos_recentes": processos}), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@dashboard_bp.route("/advogados-produtividade", methods=["GET"])
@jwt_required()
def obter_produtividade_advogados():
    """Obtenha estatísticas de produtividade dos advogados."""
    try:
        # Utiliza serviço para obter produtividade
        produtividade = DashboardService.get_advogados_produtividade()

        return jsonify({"produtividade_advogados": produtividade}), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@dashboard_bp.route("/relatorio-periodo", methods=["POST"])
@jwt_required()
def gerar_relatorio_periodo():
    """Gere relatório de processos por período específico."""
    try:
        # Obtém dados do request
        data = request.get_json()

        # Validação de campos obrigatórios
        if not data.get("data_inicio") or not data.get("data_fim"):
            return jsonify({"erro": "Data de início e fim são obrigatórias"}), 400

        # Converte datas
        try:
            data_inicio = datetime.fromisoformat(data["data_inicio"])
            data_fim = datetime.fromisoformat(data["data_fim"])
        except ValueError:
            return jsonify({"erro": "Formato de data inválido (use ISO format)"}), 400

        # Valida período
        if data_inicio > data_fim:
            return jsonify(
                {"erro": "Data de início deve ser anterior à data de fim"}
            ), 400

        # Gera relatório usando serviço
        relatorio = RelatorioService.processos_por_periodo(data_inicio, data_fim)

        return jsonify(relatorio), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500


@dashboard_bp.route("/clientes-sem-processos", methods=["GET"])
@jwt_required()
def obter_clientes_sem_processos():
    """Obtenha lista de clientes que não possuem processos associados."""
    try:
        # Utiliza serviço para obter clientes sem processos
        clientes = RelatorioService.clientes_sem_processos()

        return jsonify({"clientes_sem_processos": clientes}), 200

    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500
