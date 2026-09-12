from datetime import datetime

from pydantic import BaseModel, Field


class SolicitudPregunta(BaseModel):
    pregunta: str = Field(min_length=0, max_length=500)


class ContextoPregunta(BaseModel):
    total_criticas: int = 0
    por_categoria: dict = {}


class RespuestaPregunta(BaseModel):
    pregunta: str
    respuesta: str
    context: ContextoPregunta
    generado_en: datetime


class Perspectiva(BaseModel):
    id: int
    titulo: str
    descripcion: str
    impact: str = "medium"
    categoria: str | None = None
    generado_en: datetime


class RespuestaPerspectivas(BaseModel):
    period: str
    perspectivas: list[Perspectiva]


class FilaEvaluacion(BaseModel):
    group: str
    evaluados: int = 0
    aciertos: int = 0
    precision: float = 0.0


class RespuestaEvaluacion(BaseModel):
    total_incidencias: int
    evaluados: int
    cobertura: float
    aciertos: int
    errores: int
    precision: float
    confirmados: int
    aciertos_confirmados: int
    precision_confirmada: float
    por_fuente: list[FilaEvaluacion]
    por_categoria: list[FilaEvaluacion]
    generado_en: datetime