"""Defina schemas de validação para serialização de dados da API."""

from marshmallow import Schema, fields, validate, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.advogado import Advogado
from app.models.processo import Processo, Andamento


class UsuarioSchema(SQLAlchemyAutoSchema):
    """Defina schema para serialização de dados do modelo Usuario."""
    
    class Meta:
        model = Usuario
        exclude = ('senha_hash',)  # Nunca expor hash da senha
        load_instance = True
    
    # Validações personalizadas
    email = fields.Email(required=True)
    nome = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    tipo_usuario = fields.Str(validate=validate.OneOf(['admin', 'advogado', 'secretario', 'usuario']))


class ClienteSchema(SQLAlchemyAutoSchema):
    """Defina schema para serialização de dados do modelo Cliente."""
    
    class Meta:
        model = Cliente
        load_instance = True
    
    # Validações personalizadas
    nome = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    cpf_cnpj = fields.Str(required=True, validate=validate.Length(min=11, max=20))
    tipo_pessoa = fields.Str(required=True, validate=validate.OneOf(['fisica', 'juridica']))
    email = fields.Email(required=False, allow_none=True)
    endereco_estado = fields.Str(validate=validate.Length(equal=2), allow_none=True)


class AdvogadoSchema(SQLAlchemyAutoSchema):
    """Defina schema para serialização de dados do modelo Advogado."""
    
    class Meta:
        model = Advogado
        load_instance = True
    
    # Validações personalizadas
    nome = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    cpf = fields.Str(required=True, validate=validate.Length(equal=14))
    oab_numero = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    oab_estado = fields.Str(required=True, validate=validate.Length(equal=2))
    email = fields.Email(required=True)
    endereco_estado = fields.Str(validate=validate.Length(equal=2), allow_none=True)
    
    # Campo calculado
    oab_completa = fields.Method('get_oab_completa', dump_only=True)
    
    def get_oab_completa(self, obj):
        """Retorne OAB formatada com estado."""
        return f"OAB/{obj.oab_estado} {obj.oab_numero}"


class ProcessoSchema(SQLAlchemyAutoSchema):
    """Defina schema para serialização de dados do modelo Processo."""
    
    class Meta:
        model = Processo
        load_instance = True
        include_relationships = True
    
    # Validações personalizadas
    numero_processo = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    titulo = fields.Str(required=True, validate=validate.Length(min=5, max=200))
    area_juridica = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    status = fields.Str(validate=validate.OneOf([
        'em_andamento', 'suspenso', 'arquivado', 'finalizado',
        'aguardando_cliente', 'aguardando_documentos'
    ]))
    prioridade = fields.Str(validate=validate.OneOf(['baixa', 'normal', 'alta', 'urgente']))
    
    # Relacionamentos aninhados
    cliente = fields.Nested(ClienteSchema, dump_only=True)
    advogado_responsavel = fields.Nested(AdvogadoSchema, dump_only=True)
    
    # Campos calculados
    numero_formatado = fields.Method('get_numero_formatado', dump_only=True)
    status_descricao = fields.Method('get_status_descricao', dump_only=True)
    prioridade_descricao = fields.Method('get_prioridade_descricao', dump_only=True)
    
    def get_numero_formatado(self, obj):
        """Retorne número do processo formatado."""
        return obj.numero_formatado
    
    def get_status_descricao(self, obj):
        """Retorne descrição amigável do status."""
        return obj.status_descricao
    
    def get_prioridade_descricao(self, obj):
        """Retorne descrição amigável da prioridade."""
        return obj.prioridade_descricao


class AndamentoSchema(SQLAlchemyAutoSchema):
    """Defina schema para serialização de dados do modelo Andamento."""
    
    class Meta:
        model = Andamento
        load_instance = True
    
    # Validações personalizadas
    tipo_andamento = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    descricao = fields.Str(required=True, validate=validate.Length(min=10))
    
    # Relacionamento aninhado
    usuario = fields.Nested(UsuarioSchema, dump_only=True, exclude=('created_at', 'updated_at'))


# Schemas para requests específicos
class LoginSchema(Schema):
    """Defina schema para validação de dados de login."""
    
    email = fields.Email(required=True)
    senha = fields.Str(required=True, validate=validate.Length(min=6))


class RegistroSchema(Schema):
    """Defina schema para validação de dados de registro de usuário."""
    
    nome = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    senha = fields.Str(required=True, validate=validate.Length(min=6))
    tipo_usuario = fields.Str(validate=validate.OneOf(['admin', 'advogado', 'secretario', 'usuario']))


class BuscaSchema(Schema):
    """Defina schema para validação de parâmetros de busca."""
    
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=10)
    search = fields.Str(validate=validate.Length(max=100), missing='')
    ativo = fields.Bool(missing=True)