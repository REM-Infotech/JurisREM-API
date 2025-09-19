"""Defina o modelo Processo para gerenciamento de processos jurídicos."""

from datetime import datetime

from sqlalchemy import Numeric

from api import db
from api.models._base import BaseModel


class Processo(BaseModel):
    """Represente um processo jurídico com todas suas informações relevantes."""

    __tablename__ = "processos"

    # Identificação do processo
    numero_processo = db.Column(db.String(50), unique=True, index=True)
    numero_interno = db.Column(db.String(20), index=True)

    # Informações básicas
    titulo = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    area_juridica = db.Column(db.String(100))  # civil, criminal, trabalhista, etc.
    tipo_acao = db.Column(db.String(100))

    # Status e datas importantes
    status = db.Column(db.String(50), default="em_andamento")
    data_distribuicao = db.Column(db.Date)
    data_conclusao = db.Column(db.Date)

    # Informações do tribunal
    tribunal = db.Column(db.String(200))
    vara = db.Column(db.String(100))
    juiz = db.Column(db.String(200))

    # Valor da causa e informações financeiras
    valor_causa = db.Column(Numeric(15, 2))
    valor_honorarios = db.Column(Numeric(15, 2))
    forma_pagamento = db.Column(db.String(50))

    # Prioridade e observações
    prioridade = db.Column(
        db.String(20), default="normal"
    )  # baixa, normal, alta, urgente
    observacoes = db.Column(db.Text)
    observacoes_internas = db.Column(db.Text)

    # Relacionamentos com outras entidades
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"))
    advogado_id = db.Column(db.Integer, db.ForeignKey("advogados.id"))

    # Relacionamento com andamentos do processo
    andamentos = db.relationship(
        "Andamento", backref="processo", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def numero_formatado(self):
        """Retorne o número do processo formatado para exibição."""
        # Remove caracteres não numéricos para formatação
        numeros = "".join(filter(str.isdigit, self.numero_processo))

        if len(numeros) == 20:  # Formato padrão CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO
            return f"{numeros[:7]}-{numeros[7:9]}.{numeros[9:13]}.{numeros[13]}.{numeros[14:16]}.{numeros[16:]}"
        else:
            return self.numero_processo

    @property
    def status_descricao(self):
        """Retorne descrição amigável do status do processo."""
        status_map = {
            "em_andamento": "Em Andamento",
            "suspenso": "Suspenso",
            "arquivado": "Arquivado",
            "finalizado": "Finalizado",
            "aguardando_cliente": "Aguardando Cliente",
            "aguardando_documentos": "Aguardando Documentos",
        }
        return status_map.get(self.status, self.status.title())

    @property
    def prioridade_descricao(self):
        """Retorne descrição amigável da prioridade do processo."""
        prioridade_map = {
            "baixa": "Baixa",
            "normal": "Normal",
            "alta": "Alta",
            "urgente": "Urgente",
        }
        return prioridade_map.get(self.prioridade, self.prioridade.title())

    def get_ultimo_andamento(self):
        """Retorne o andamento mais recente do processo."""
        from api.models.processo import (
            Andamento,  # Import local para evitar circular import
        )

        return self.andamentos.order_by(Andamento.data_andamento.desc()).first()

    def __repr__(self):
        """Retorne representação string do objeto Processo."""
        return f"<Processo {self.numero_processo} - {self.titulo[:50]}>"


class Andamento(BaseModel):
    """Represente um andamento ou movimentação de um processo jurídico."""

    __tablename__ = "andamentos"

    # Informações do andamento
    data_andamento = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_andamento = db.Column(db.String(100))
    descricao = db.Column(db.Text)

    # Informações complementares
    observacoes = db.Column(db.Text)
    documento_anexo = db.Column(db.String(500))  # caminho para arquivo anexo

    # Relacionamento com processo
    processo_id = db.Column(db.Integer, db.ForeignKey("processos.id"))

    # Usuário responsável pelo andamento
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    usuario = db.relationship("Usuario", backref="andamentos_criados")

    def __repr__(self):
        """Retorne representação string do objeto Andamento."""
        return f"<Andamento {self.tipo_andamento} - {self.data_andamento.strftime('%d/%m/%Y')}>"
