"""Defina o modelo Advogado para gerenciamento da equipe jurídica."""

from app import db
from app.models import BaseModel


class Advogado(BaseModel):
    """Represente um advogado responsável por processos jurídicos."""
    
    __tablename__ = 'advogados'
    
    # Informações pessoais e profissionais
    nome = db.Column(db.String(200), nullable=False, index=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    oab_numero = db.Column(db.String(20), unique=True, nullable=False, index=True)
    oab_estado = db.Column(db.String(2), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    
    # Especialidades jurídicas
    especialidades = db.Column(db.Text, nullable=True)  # JSON string com lista de especialidades
    
    # Status profissional
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_admissao = db.Column(db.Date, nullable=True)
    data_demissao = db.Column(db.Date, nullable=True)
    
    # Endereço profissional
    endereco_rua = db.Column(db.String(200), nullable=True)
    endereco_numero = db.Column(db.String(10), nullable=True)
    endereco_complemento = db.Column(db.String(100), nullable=True)
    endereco_bairro = db.Column(db.String(100), nullable=True)
    endereco_cidade = db.Column(db.String(100), nullable=True)
    endereco_estado = db.Column(db.String(2), nullable=True)
    endereco_cep = db.Column(db.String(10), nullable=True)
    
    # Informações complementares
    biografia = db.Column(db.Text, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    
    # Relacionamento com processos (um advogado pode ter vários processos)
    processos = db.relationship('Processo', backref='advogado_responsavel', lazy=True)
    
    @property
    def oab_completa(self):
        """Retorne o número da OAB formatado com estado."""
        return f"OAB/{self.oab_estado} {self.oab_numero}"
    
    @property
    def endereco_completo(self):
        """Retorne o endereço completo formatado do advogado."""
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
            
        return ''.join(endereco_parts) if endereco_parts else None
    
    def get_especialidades_list(self):
        """Retorne lista de especialidades do advogado."""
        import json
        try:
            return json.loads(self.especialidades) if self.especialidades else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_especialidades_list(self, especialidades_list):
        """Defina especialidades do advogado a partir de uma lista."""
        import json
        self.especialidades = json.dumps(especialidades_list) if especialidades_list else None
    
    def __repr__(self):
        """Retorne representação string do objeto Advogado."""
        return f'<Advogado {self.nome} - {self.oab_completa}>'