"""Configure ambiente de testes para a aplicação JurisREM API."""

import pytest  # type: ignore # noqa: F401

from api import create_app, db
from api.models.advogado import Advogado
from api.models.cliente import Cliente
from api.models.processo import Processo  # noqa: F401
from api.models.usuario import Usuario


@pytest.fixture
def app():
    """Crie instância da aplicação configurada para testes."""
    # Cria aplicação em modo de teste
    app = create_app("testing")

    # Configura contexto da aplicação
    with app.app_context():
        # Cria todas as tabelas
        db.create_all()

        yield app

        # Limpa dados após os testes
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Crie cliente de teste para requisições HTTP."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Crie runner para comandos CLI da aplicação."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Crie headers de autenticação com usuário de teste."""
    # Cria usuário de teste
    usuario_teste = Usuario(
        nome="Usuário Teste",
        email="teste@exemplo.com",
        tipo_usuario="admin",
        ativo=True,
    )
    usuario_teste.set_password("senha123")
    usuario_teste.save()

    # Faz login e obtém token
    response = client.post(
        "/api/auth/login", json={"email": "teste@exemplo.com", "senha": "senha123"}
    )

    token = response.get_json()["token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def cliente_teste():
    """Crie cliente de teste para usar nos testes."""
    cliente = Cliente(
        nome="Cliente Teste",
        cpf_cnpj="123.456.789-00",
        tipo_pessoa="fisica",
        email="cliente@teste.com",
        telefone="(11) 99999-9999",
    )
    cliente.save()
    return cliente


@pytest.fixture
def advogado_teste():
    """Crie advogado de teste para usar nos testes."""
    advogado = Advogado(
        nome="Dr. Advogado Teste",
        cpf="987.654.321-00",
        oab_numero="123456",
        oab_estado="SP",
        email="advogado@teste.com",
    )
    advogado.save()
    return advogado
