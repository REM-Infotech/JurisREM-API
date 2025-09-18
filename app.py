"""Execute a aplicação Flask JurisREM API."""

import os
from app import create_app, db
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.advogado import Advogado
from app.models.processo import Processo, Andamento
from flask_migrate import upgrade

# Cria instância da aplicação baseada na configuração do ambiente
config_name = os.environ.get('FLASK_ENV', 'default')
app = create_app(config_name)


@app.cli.command()
def init_db():
    """Initialize banco de dados criando todas as tabelas necessárias."""
    # Cria todas as tabelas definidas nos modelos
    db.create_all()
    print("Banco de dados inicializado com sucesso!")


@app.cli.command()
def create_admin():
    """Crie um usuário administrador padrão para acesso inicial."""
    # Verifica se já existe usuário admin
    admin_existente = Usuario.query.filter_by(email='admin@jurisrem.com').first()
    
    if admin_existente:
        print("Usuário administrador já existe!")
        return
    
    # Cria usuário administrador
    admin = Usuario(
        nome='Administrador',
        email='admin@jurisrem.com',
        tipo_usuario='admin',
        ativo=True
    )
    admin.set_password('admin123')  # Senha padrão - deve ser alterada
    
    # Salva no banco de dados
    admin.save()
    print("Usuário administrador criado com sucesso!")
    print("Email: admin@jurisrem.com")
    print("Senha: admin123")
    print("IMPORTANTE: Altere a senha padrão após o primeiro login!")


@app.cli.command()
def seed_data():
    """Popule o banco de dados com dados de exemplo para desenvolvimento."""
    # Cria clientes de exemplo
    cliente1 = Cliente(
        nome='João Silva Santos',
        cpf_cnpj='123.456.789-00',
        tipo_pessoa='fisica',
        email='joao.silva@email.com',
        telefone='(11) 99999-9999',
        endereco_rua='Rua das Flores, 123',
        endereco_bairro='Centro',
        endereco_cidade='São Paulo',
        endereco_estado='SP',
        endereco_cep='01234-567'
    )
    
    cliente2 = Cliente(
        nome='Empresa Exemplo LTDA',
        cpf_cnpj='12.345.678/0001-90',
        tipo_pessoa='juridica',
        email='contato@empresaexemplo.com',
        telefone='(11) 3333-3333',
        endereco_rua='Av. Paulista, 1000',
        endereco_bairro='Bela Vista',
        endereco_cidade='São Paulo',
        endereco_estado='SP',
        endereco_cep='01310-100'
    )
    
    # Cria advogado de exemplo
    advogado1 = Advogado(
        nome='Dr. Maria Oliveira',
        cpf='987.654.321-00',
        oab_numero='123456',
        oab_estado='SP',
        email='maria.oliveira@jurisrem.com',
        telefone='(11) 88888-8888'
    )
    advogado1.set_especialidades_list(['Direito Civil', 'Direito Empresarial'])
    
    # Salva dados de exemplo
    cliente1.save()
    cliente2.save()
    advogado1.save()
    
    print("Dados de exemplo criados com sucesso!")


@app.shell_context_processor
def make_shell_context():
    """Configure contexto do shell Flask com modelos importados."""
    return {
        'db': db,
        'Usuario': Usuario,
        'Cliente': Cliente,
        'Advogado': Advogado,
        'Processo': Processo,
        'Andamento': Andamento
    }


@app.route('/')
def index():
    """Exiba informações básicas da API na rota raiz."""
    return {
        'nome': 'JurisREM API',
        'versao': '1.0.0',
        'descricao': 'API REST para gerenciamento de processos jurídicos',
        'documentacao': '/api/docs',
        'status': 'online'
    }


@app.route('/api/health')
def health_check():
    """Verifique status de saúde da aplicação."""
    try:
        # Testa conexão com banco de dados
        db.session.execute(db.text('SELECT 1'))
        db_status = 'ok'
    except Exception:
        db_status = 'erro'
    
    return {
        'status': 'ok' if db_status == 'ok' else 'erro',
        'database': db_status,
        'timestamp': str(db.func.now())
    }


if __name__ == '__main__':
    # Executa aplicação em modo debug se executada diretamente
    app.run(debug=True, host='0.0.0.0', port=5000)