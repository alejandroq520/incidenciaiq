"""Endpoints REST de incidencias."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.base_de_datos import get_db
from app.schemas.incidencia import (
    ActualizarIncidencia,
    CrearIncidencia,
    LecturaIncidencia,
    RespuestaListaIncidencias,
    SolicitudConfirmarAnalisis,
)
from app.services import servicio_ia, servicio_incidencias
from app.utils.logger import get_logger

logger = get_logger("incidencias")

router = APIRouter(prefix="/api/incidencias", tags=["incidencias"])


def _parse_ids(value: str | None) -> list[int] | None:
    if not value:
        return None
    ids = [int(x) for x in value.split(",") if x.strip().isdigit()]
    return ids or None


@router.post("", response_model=LecturaIncidencia, status_code=201)
def crear_incidencia(data: CrearIncidencia, db: Session = Depends(get_db)):
    incidencia = servicio_incidencias.crear_incidencia(db, data)
    analisis = servicio_ia.clasificar_incidencia(db, incidencia)
    if analisis:
        logger.info("Clasificación IA guardada para INC-%s", incidencia.id)
    return servicio_incidencias.a_dict_lectura(
        servicio_incidencias.obtener_incidencia_por_id(db, incidencia.id)
    )


@router.get("", response_model=RespuestaListaIncidencias)
def listar_incidencias(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    estado_id: str | None = Query(default=None, description="CSV de ids"),
    prioridad_id: str | None = Query(default=None, description="CSV de ids"),
    categoria_id: str | None = Query(default=None, description="CSV de ids"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    search: str | None = Query(default=None, max_length=200),
    sort_by: str = Query(default="creado_en"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
):
    return servicio_incidencias.obtener_incidencias(
        db,
        skip=skip,
        limit=limit,
        estado_ids=_parse_ids(estado_id),
        prioridad_ids=_parse_ids(prioridad_id),
        categoria_ids=_parse_ids(categoria_id),
        date_from=date_from,
        date_to=date_to,
        search=search,
        sort_by=sort_by,
        order=order,
    )


@router.get("/{incidencia_id}", response_model=LecturaIncidencia)
def obtener_incidencia(incidencia_id: int, db: Session = Depends(get_db)):
    return servicio_incidencias.a_dict_lectura(
        servicio_incidencias.obtener_incidencia_por_id(db, incidencia_id)
    )


@router.put("/{incidencia_id}", response_model=LecturaIncidencia)
def actualizar_incidencia(
    incidencia_id: int,
    updates: ActualizarIncidencia,
    db: Session = Depends(get_db),
):
    cambiado_por = updates.creado_por or "Sistema Demo"
    return servicio_incidencias.a_dict_lectura(
        servicio_incidencias.actualizar_incidencia(db, incidencia_id, updates, cambiado_por)
    )


@router.put("/{incidencia_id}/analisis-ia/confirmar", response_model=LecturaIncidencia)
def confirmar_analisis(
    incidencia_id: int,
    body: SolicitudConfirmarAnalisis,
    db: Session = Depends(get_db),
):
    return servicio_incidencias.a_dict_lectura(
        servicio_incidencias.confirmar_analisis_ia(db, incidencia_id, body.confirmado)
    )