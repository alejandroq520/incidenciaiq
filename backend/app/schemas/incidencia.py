from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LecturaCategoria(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    descripcion: str | None = None
    color: str = "#3B82F6"
    icon: str | None = None


class LecturaPrioridad(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    level: int = 1
    color: str = "#6B7280"
    icon: str | None = None


class LecturaEstado(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    descripcion: str | None = None
    color: str = "#6B7280"


class CrearIncidencia(BaseModel):
    titulo: str = Field(min_length=5, max_length=255)
    descripcion: str = Field(min_length=10, max_length=1000)
    categoria_id: int = Field(ge=1)
    prioridad_id: int = Field(ge=1)
    creado_por: str | None = Field(default="Sistema Demo", max_length=100)


class ActualizarIncidencia(BaseModel):
    estado_id: int | None = Field(default=None, ge=1)
    prioridad_id: int | None = Field(default=None, ge=1)
    categoria_id: int | None = Field(default=None, ge=1)
    notas: str | None = Field(default=None, max_length=2000)
    creado_por: str | None = Field(default=None, max_length=100)


class SolicitudConfirmarAnalisis(BaseModel):
    confirmado: bool = True


class LecturaAnalisisIA(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    categoria_sugerida: str | None = None
    prioridad_sugerida: str | None = None
    resumen: str | None = None
    recomendacion: str | None = None
    confianza: float = 0.0
    creado_en: datetime
    confirmado: bool = False
    fuente: str = "heuristic"
    justificacion: str | None = None
    incidencia_referencia_id: int | None = None
    indice_similitud: float | None = None


class LecturaHistorial(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    fecha: datetime
    accion: str
    valor_anterior: str | None = None
    valor_nuevo: str | None = None
    cambiado_por: str


class LecturaIncidencia(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    descripcion: str
    categoria: LecturaCategoria
    prioridad: LecturaPrioridad
    estado: LecturaEstado
    creado_en: datetime
    actualizado_en: datetime
    creado_por: str
    notas: str | None = None
    tiempo_resolucion_minutos: int | None = None
    resuelto_en: datetime | None = None
    analisis_ia: LecturaAnalisisIA | None = None
    historial: list[LecturaHistorial] = Field(default_factory=list)


class ElementoListaIncidencia(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    estado: str
    prioridad: str
    categoria: str
    nivel_prioridad: int = 0
    creado_en: datetime
    actualizado_en: datetime


class RespuestaListaIncidencias(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[ElementoListaIncidencia]