"""Defina o modelo Cliente para gerenciamento de clientes jurídicos."""

from api import db
from api.models._base import BaseModel


class Cliente(BaseModel):
    """Represente um cliente que pode ter processos jurídicos associados."""

    __tablename__ = "clientes"

    # Informações pessoais básicas
    nome = db.Column(db.String(200), nullable=False, index=True)
    cpf_cnpj = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)

    # Tipo de pessoa (física ou jurídica)
    tipo_pessoa = db.Column(db.String(20), nullable=False, default="fisica")

    # Endereço completo do cliente
    endereco_rua = db.Column(db.String(200), nullable=True)
    endereco_numero = db.Column(db.String(10), nullable=True)
    endereco_complemento = db.Column(db.String(100), nullable=True)
    endereco_bairro = db.Column(db.String(100), nullable=True)
    endereco_cidade = db.Column(db.String(100), nullable=True)
    endereco_estado = db.Column(db.String(2), nullable=True)
    endereco_cep = db.Column(db.String(10), nullable=True)

    # Informações adicionais
    profissao = db.Column(db.String(100), nullable=True)
    estado_civil = db.Column(db.String(50), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    # Relacionamento com processos
    processos = db.relationship("Processo", backref="cliente", lazy=True)

    @property
    def endereco_completo(self):
        """Retorne o endereço completo formatado do cliente."""
        # Monta endereço completo a partir dos campos individuais
        endereco_parts = []

        if self.endereco_rua:
            endereco_parts.append(self.endereco_rua)
        if self.endereco_numero:
            endereco_parts.append(f", {self.endereco_numero}")
        if self.endereco_complemento:
            endereco_parts.append(f", {self.endereco_complemento}")
        if self.endereco_bairro:
            endereco_parts.append(f" - {self.endereco_bairro}")
        if self.endereco_cidade:
            endereco_parts.append(f", {self.endereco_cidade}")
        if self.endereco_estado:
            endereco_parts.append(f"/{self.endereco_estado}")
        if self.endereco_cep:
            endereco_parts.append(f" - CEP: {self.endereco_cep}")

        return "".join(endereco_parts) if endereco_parts else None

    def __repr__(self):
        """Retorne representação string do objeto Cliente."""
        return f"<Cliente {self.nome} - {self.cpf_cnpj}>"
