from datetime import datetime

from pydantic import BaseModel, Field


class RespuestaMetricas(BaseModel):
    period: str
    date_from: datetime
    date_to: datetime
    total_incidencias: int
    opened_incidencias: int
    closed_incidencias: int
    critical_incidencias: int
    average_resolution_time_hours: float
    sla_compliance_percentage: float
    recurring_patterns: int
    comparison: dict


class ElementoDesgloseCategoria(BaseModel):
    id: int
    name: str
    total: int
    opened: int
    closed: int
    percentage: float
    color: str


class RespuestaDesgloseCategorias(BaseModel):
    period: str
    categorias: list[ElementoDesgloseCategoria] = Field(default_factory=list)


class PuntoTendencia(BaseModel):
    date: str
    created: int
    closed: int
    opened: int


class RespuestaTendencia(BaseModel):
    period: str
    granularity: str
    data: list[PuntoTendencia] = Field(default_factory=list)


class FilaResolucionCategoria(BaseModel):
    categoria: str
    average_hours: float


class FilaResolucionPrioridad(BaseModel):
    prioridad: str
    average_hours: float


class RespuestaTiempoResolucion(BaseModel):
    period: str
    average_hours: float
    median_hours: float
    min_hours: float
    max_hours: float
    p95_hours: float
    por_categoria: list[FilaResolucionCategoria] = Field(default_factory=list)
    por_prioridad: list[FilaResolucionPrioridad] = Field(default_factory=list)