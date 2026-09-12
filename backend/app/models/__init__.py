"""Modelos ORM."""

from app.models.analisis_ia import AnalisisIA
from app.models.categoria import Categoria
from app.models.estado import Estado
from app.models.historial_incidencia import HistorialIncidencia
from app.models.incidencia import Incidencia
from app.models.prioridad import Prioridad

__all__ = [
    "Categoria",
    "Prioridad",
    "Estado",
    "Incidencia",
    "HistorialIncidencia",
    "AnalisisIA",
]