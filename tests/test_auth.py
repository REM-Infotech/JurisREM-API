"""Teste funcionalidades de autenticação da API."""

import pytest
from app.models.usuario import Usuario


def test_login_sucesso(client):
    """Teste login com credenciais válidas."""
    # Cria usuário de teste
    usuario = Usuario(
        nome='Teste Login',
        email='login@teste.com',
        tipo_usuario='usuario',
        ativo=True
    )
    usuario.set_password('senha123')
    usuario.save()
    
    # Tenta fazer login
    response = client.post('/api/auth/login', json={
        'email': 'login@teste.com',
        'senha': 'senha123'
    })
    
    # Verifica resposta
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert data['usuario']['email'] == 'login@teste.com'


def test_login_credenciais_invalidas(client):
    """Teste login com credenciais inválidas."""
    response = client.post('/api/auth/login', json={
        'email': 'inexistente@teste.com',
        'senha': 'senhaerrada'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'erro' in data


def test_registro_usuario(client):
    """Teste registro de novo usuário."""
    response = client.post('/api/auth/registro', json={
        'nome': 'Novo Usuario',
        'email': 'novo@teste.com',
        'senha': 'senha123',
        'tipo_usuario': 'usuario'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['usuario']['email'] == 'novo@teste.com'


def test_perfil_autenticado(client, auth_headers):
    """Teste acesso ao perfil com autenticação."""
    response = client.get('/api/auth/perfil', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'email' in data


def test_perfil_sem_autenticacao(client):
    """Teste acesso ao perfil sem autenticação."""
    response = client.get('/api/auth/perfil')
    
    assert response.status_code == 401  # JWT missing returns 401