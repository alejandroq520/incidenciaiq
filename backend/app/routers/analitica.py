"""Endpoints de analítica y métricas."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.base_de_datos import get_db
from app.schemas.analitica import (
    RespuestaDesgloseCategorias,
    RespuestaMetricas,
    RespuestaTendencia,
    RespuestaTiempoResolucion,
)
from app.services import servicio_analitica

router = APIRouter(prefix="/api/analitica", tags=["analitica"])


@router.get("/metricas", response_model=RespuestaMetricas)
def obtener_metricas(
    period: str = Query(default="7d"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return servicio_analitica.obtener_metricas(db, period, date_from, date_to)


@router.get("/por-categoria", response_model=RespuestaDesgloseCategorias)
def obtener_por_categoria(
    period: str = Query(default="7d"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return servicio_analitica.obtener_por_categoria(db, period, date_from, date_to)


@router.get("/tendencia", response_model=RespuestaTendencia)
def obtener_tendencia(
    period: str = Query(default="7d"),
    granularity: str = Query(default="daily"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if granularity not in ("daily", "hourly"):
        granularity = "daily"
    return servicio_analitica.obtener_tendencia(db, period, granularity, date_from, date_to)


@router.get("/tiempo-resolucion", response_model=RespuestaTiempoResolucion)
def obtener_tiempos_resolucion(
    period: str = Query(default="7d"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return servicio_analitica.obtener_tiempos_resolucion(db, period, date_from, date_to)