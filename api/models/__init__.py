"""Defina modelos base e importações centrais para toda aplicação."""

from datetime import datetime

from api.models import advogado, cliente, processo, usuario

__all__ = ["datetime", "cliente", "advogado", "processo", "usuario"]
