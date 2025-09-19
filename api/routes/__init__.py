from flask import Response, jsonify
from werkzeug.exceptions import HTTPException

from api import app


@app.after_request
def after_party(response: Response) -> Response:
    _resp = response

    _resp.headers["Access-Control-Allow-Origin"] = "*"
    _resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return _resp


@app.errorhandler(400)
def bad_request(error: HTTPException) -> Response:
    """Trate erros de requisição inválida (400 Bad Request)."""
    return jsonify(
        {
            "erro": "Requisição inválida",
            "codigo": 400,
            "detalhes": error.description if hasattr(error, "description") else None,
        }
    ), 400


@app.errorhandler(401)
def unauthorized(error: HTTPException) -> Response:
    """Trate erros de acesso não autorizado (401 Unauthorized)."""
    return jsonify(
        {
            "erro": "Acesso não autorizado",
            "codigo": 401,
            "mensagem": "Token de autenticação necessário",
        }
    ), 401


@app.errorhandler(403)
def forbidden(error: HTTPException) -> Response:
    """Trate erros de acesso proibido (403 Forbidden)."""
    return jsonify(
        {
            "erro": "Acesso proibido",
            "codigo": 403,
            "mensagem": "Usuário não possui permissão para este recurso",
        }
    ), 403


@app.errorhandler(404)
def not_found(error: HTTPException) -> Response:
    """Trate erros de recurso não encontrado (404 Not Found)."""
    return jsonify(
        {
            "erro": "Recurso não encontrado",
            "codigo": 404,
            "mensagem": "O recurso solicitado não foi encontrado",
        }
    ), 404


@app.errorhandler(405)
def method_not_allowed(error: HTTPException) -> Response:
    """Trate erros de método não permitido (405 Method Not Allowed)."""
    return jsonify(
        {
            "erro": "Método não permitido",
            "codigo": 405,
            "mensagem": "Método HTTP não permitido para este endpoint",
        }
    ), 405


@app.errorhandler(409)
def conflict(error: HTTPException) -> Response:
    """Trate erros de conflito de dados (409 Conflict)."""
    return jsonify(
        {
            "erro": "Conflito de dados",
            "codigo": 409,
            "detalhes": error.description if hasattr(error, "description") else None,
        }
    ), 409


@app.errorhandler(422)
def unprocessable_entity(error: HTTPException) -> Response:
    """Trate erros de entidade não processável (422 Unprocessable Entity)."""
    return jsonify(
        {
            "erro": "Dados inválidos",
            "codigo": 422,
            "detalhes": error.description if hasattr(error, "description") else None,
        }
    ), 422


@app.errorhandler(500)
def internal_server_error(error: HTTPException) -> Response:
    """Trate erros internos do servidor (500 Internal Server Error)."""
    # Log do erro para debugging (seria melhor usar um logger configurado)
    print(f"Erro interno do servidor: {error}")

    return jsonify(
        {
            "erro": "Erro interno do servidor",
            "codigo": 500,
            "mensagem": "Ocorreu um erro inesperado. Tente novamente mais tarde.",
        }
    ), 500


@app.errorhandler(HTTPException)
def handle_http_exception(error: HTTPException) -> Response:
    """Trate outras exceções HTTP não capturadas especificamente."""
    return jsonify(
        {"erro": error.name, "codigo": error.code, "mensagem": error.description}
    ), error.code


@app.errorhandler(Exception)
def handle_generic_exception(error: HTTPException) -> Response:
    """Trate exceções genéricas não capturadas pelos outros handlers."""
    # Log do erro para debugging
    print(f"Exceção não tratada: {type(HTTPException).__name__}: {error}")

    return jsonify(
        {
            "erro": "Erro interno do servidor",
            "codigo": 500,
            "mensagem": "Ocorreu um erro inesperado. Tente novamente mais tarde.",
        }
    ), 500
