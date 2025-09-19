"""Defina serviços base e utilitários para a aplicação."""

from datetime import datetime, timedelta  # noqa: F401

from sqlalchemy import and_, func, or_  # noqa: F401

from api import db
from api.models.advogado import Advogado
from api.models.cliente import Cliente
from api.models.processo import Processo


class DashboardService:
    """Forneça dados estatísticos para dashboard administrativo."""

    @staticmethod
    def get_estatisticas_gerais():
        """Obtenha estatísticas gerais do sistema.

        Returns:
            dict: Dicionário com estatísticas gerais
        """
        # Contagem total de registros
        total_clientes = Cliente.query.filter_by(ativo=True).count()
        total_advogados = Advogado.query.filter_by(ativo=True).count()
        total_processos = Processo.query.count()

        # Processos por status
        processos_por_status = (
            db.session.query(Processo.status, func.count(Processo.id).label("total"))
            .group_by(Processo.status)
            .all()
        )

        # Processos por área jurídica
        processos_por_area = (
            db.session.query(
                Processo.area_juridica, func.count(Processo.id).label("total")
            )
            .group_by(Processo.area_juridica)
            .all()
        )

        # Processos por prioridade
        processos_por_prioridade = (
            db.session.query(
                Processo.prioridade, func.count(Processo.id).label("total")
            )
            .group_by(Processo.prioridade)
            .all()
        )

        return {
            "totais": {
                "clientes": total_clientes,
                "advogados": total_advogados,
                "processos": total_processos,
            },
            "processos_por_status": [
                {"status": r.status, "total": r.total} for r in processos_por_status
            ],
            "processos_por_area": [
                {"area": r.area_juridica, "total": r.total} for r in processos_por_area
            ],
            "processos_por_prioridade": [
                {"prioridade": r.prioridade, "total": r.total}
                for r in processos_por_prioridade
            ],
        }

    @staticmethod
    def get_processos_recentes(limite=10):
        """Obtenha lista dos processos mais recentes.

        Args:
            limite (int): Número máximo de processos a retornar

        Returns:
            list: Lista de processos recentes
        """
        # Busca processos mais recentes com relacionamentos
        processos = (
            Processo.query.join(Cliente)
            .join(Advogado)
            .order_by(Processo.created_at.desc())
            .limit(limite)
            .all()
        )

        processos_data = []
        for processo in processos:
            processos_data.append(
                {
                    "id": processo.id,
                    "numero_processo": processo.numero_processo,
                    "titulo": processo.titulo,
                    "status": processo.status,
                    "cliente_nome": processo.cliente.nome,
                    "advogado_nome": processo.advogado_responsavel.nome,
                    "created_at": processo.created_at.isoformat(),
                }
            )

        return processos_data

    @staticmethod
    def get_advogados_produtividade():
        """Obtenha estatísticas de produtividade dos advogados.

        Returns:
            list: Lista com produtividade por advogado
        """
        # Query para contar processos por advogado
        resultado = (
            db.session.query(
                Advogado.id,
                Advogado.nome,
                Advogado.oab_numero,
                Advogado.oab_estado,
                func.count(Processo.id).label("total_processos"),
            )
            .join(Processo, Advogado.id == Processo.advogado_id)
            .filter(Advogado.ativo == True)  # noqa: E712
            .group_by(
                Advogado.id, Advogado.nome, Advogado.oab_numero, Advogado.oab_estado
            )
            .order_by(func.count(Processo.id).desc())
            .all()
        )

        produtividade_data = []
        for r in resultado:
            produtividade_data.append(
                {
                    "advogado_id": r.id,
                    "nome": r.nome,
                    "oab_completa": f"OAB/{r.oab_estado} {r.oab_numero}",
                    "total_processos": r.total_processos,
                }
            )

        return produtividade_data


class RelatorioService:
    """Forneça serviços para geração de relatórios."""

    @staticmethod
    def processos_por_periodo(data_inicio, data_fim):
        """Gere relatório de processos criados em um período específico.

        Args:
            data_inicio (datetime): Data de início do período
            data_fim (datetime): Data de fim do período

        Returns:
            dict: Relatório com dados do período
        """
        # Filtra processos no período especificado
        processos = (
            Processo.query.filter(
                and_(
                    Processo.created_at >= data_inicio, Processo.created_at <= data_fim
                )
            )
            .join(Cliente)
            .join(Advogado)
            .all()
        )

        # Compila estatísticas do período
        total_processos = len(processos)
        areas_juridicas = {}
        status_processos = {}
        advogados_atuacao = {}

        valor_total_causas = 0

        for processo in processos:
            # Conta por área jurídica
            area = processo.area_juridica
            areas_juridicas[area] = areas_juridicas.get(area, 0) + 1

            # Conta por status
            status = processo.status
            status_processos[status] = status_processos.get(status, 0) + 1

            # Conta por advogado
            advogado = processo.advogado_responsavel.nome
            advogados_atuacao[advogado] = advogados_atuacao.get(advogado, 0) + 1

            # Soma valores das causas
            if processo.valor_causa:
                valor_total_causas += float(processo.valor_causa)

        return {
            "periodo": {
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat(),
            },
            "totais": {
                "processos": total_processos,
                "valor_total_causas": valor_total_causas,
            },
            "distribuicao": {
                "areas_juridicas": areas_juridicas,
                "status_processos": status_processos,
                "advogados_atuacao": advogados_atuacao,
            },
        }

    @staticmethod
    def clientes_sem_processos():
        """Identifique clientes que não possuem processos associados.

        Returns:
            list: Lista de clientes sem processos
        """
        # Busca clientes ativos sem processos
        clientes = Cliente.query.filter(
            and_(
                Cliente.ativo == True,  # noqa: E712
                ~Cliente.id.in_(db.session.query(Processo.cliente_id).distinct()),
            )
        ).all()

        clientes_data = []
        for cliente in clientes:
            clientes_data.append(
                {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "cpf_cnpj": cliente.cpf_cnpj,
                    "email": cliente.email,
                    "telefone": cliente.telefone,
                    "created_at": cliente.created_at.isoformat(),
                }
            )

        return clientes_data
