from typing import TypedDict


class ProcessoInterface(TypedDict):
    numero_processo: str
    titulo: str
    area_juridica: str
    cliente_id: str
    advogado_id: str
