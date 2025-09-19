"""Defina modelos base e importações centrais para toda aplicação."""

from datetime import datetime

from app.models import advogado, cliente, processo, usuario

__all__ = ["datetime", "cliente", "advogado", "processo", "usuario"]
