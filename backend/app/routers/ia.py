"""Endpoints de IA: preguntas al asistente, perspectivas automáticas y evaluación del clasificador."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.base_de_datos import get_db
from app.schemas.ia import (
    RespuestaEvaluacion,
    RespuestaPerspectivas,
    RespuestaPregunta,
    SolicitudPregunta,
)
from app.services import servicio_evaluacion, servicio_ia

router = APIRouter(prefix="/api/ia", tags=["ia"])


@router.post("/preguntar", response_model=RespuestaPregunta)
def preguntar(body: SolicitudPregunta, db: Session = Depends(get_db)):
    return servicio_ia.responder_pregunta(db, body.pregunta)


@router.get("/perspectivas", response_model=RespuestaPerspectivas)
def obtener_perspectivas(
    limit: int = Query(default=4, ge=1, le=10),
    period: str = Query(default="7d"),
    db: Session = Depends(get_db),
):
    perspectivas = servicio_ia.generar_perspectivas(db, period)
    return {"period": period, "perspectivas": perspectivas[:limit]}


@router.get("/evaluacion", response_model=RespuestaEvaluacion)
def obtener_evaluacion(db: Session = Depends(get_db)):
    return servicio_evaluacion.obtener_evaluacion(db)