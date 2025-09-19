"""Defina rotas gerais da aplicação (raiz e health check)."""

from flask import Blueprint, jsonify
from app import db

# Cria blueprint para rotas gerais
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Exiba informações básicas da API na rota raiz."""
    return jsonify({
        'nome': 'JurisREM API',
        'versao': '1.0.0',
        'descricao': 'API REST para gerenciamento de processos jurídicos',
        'documentacao': '/api/docs',
        'status': 'online'
    })


@main_bp.route('/api/health')
def health_check():
    """Verifique status de saúde da aplicação."""
    try:
        # Testa conexão com banco de dados
        db.session.execute(db.text('SELECT 1'))
        db_status = 'ok'
    except Exception:
        db_status = 'erro'
    
    return jsonify({
        'status': 'ok' if db_status == 'ok' else 'erro',
        'database': db_status,
        'message': 'API is running'
    })