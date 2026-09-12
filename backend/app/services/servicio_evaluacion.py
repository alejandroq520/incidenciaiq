"""Evaluación del clasificador calculada exclusivamente con datos reales.

Verdad de referencia: la categoría realmente asignada/resuelta de cada incidencia.
Predicciones: la categoría sugerida por la capa de IA (reglas / GPT / casos).
Todas las cifras (precisión, cobertura, aciertos/errores, por fuente, por categoría)
se calculan a partir de filas almacenadas, nunca fabricadas.
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import AnalisisIA, Incidencia


def _precision(pairs) -> dict:
    n = len(pairs)
    ok = sum(
        1
        for analisis, _ in pairs
        if analisis.categoria_sugerida is not None
        and analisis.incidencia.categoria is not None
        and analisis.categoria_sugerida.name == analisis.incidencia.categoria.name
    )
    return {"evaluados": n, "aciertos": ok, "precision": round(ok / n, 4) if n else 0.0}


def obtener_evaluacion(db: Session) -> dict:
    total_incidencias = db.scalar(select(func.count()).select_from(Incidencia)) or 0

    analyses = db.scalars(
        select(AnalisisIA).options(
            selectinload(AnalisisIA.incidencia).selectinload(Incidencia.categoria),
            selectinload(AnalisisIA.categoria_sugerida),
        )
    ).all()

    evaluable = [
        a for a in analyses if a.categoria_sugerida is not None and a.incidencia.categoria is not None
    ]
    overall = _precision([(a, True) for a in evaluable])

    confirmados = [a for a in evaluable if a.confirmado]
    confirmados_stats = _precision([(a, True) for a in confirmados])

    por_fuente: dict[str, list] = {}
    for a in evaluable:
        por_fuente.setdefault(a.fuente, []).append(a)
    fuente_rows = [
        {
            "group": fuente,
            "evaluados": len(group),
            "aciertos": _precision([(a, True) for a in group])["aciertos"],
            "precision": _precision([(a, True) for a in group])["precision"],
        }
        for fuente, group in sorted(por_fuente.items())
    ]

    por_categoria: dict[str, list] = {}
    for a in evaluable:
        por_categoria.setdefault(a.incidencia.categoria.name, []).append(a)
    categoria_rows = [
        {
            "group": name,
            "evaluados": len(group),
            "aciertos": _precision([(a, True) for a in group])["aciertos"],
            "precision": _precision([(a, True) for a in group])["precision"],
        }
        for name, group in sorted(por_categoria.items())
    ]

    return {
        "total_incidencias": total_incidencias,
        "evaluados": overall["evaluados"],
        "cobertura": round(overall["evaluados"] / total_incidencias, 4) if total_incidencias else 0.0,
        "aciertos": overall["aciertos"],
        "errores": overall["evaluados"] - overall["aciertos"],
        "precision": overall["precision"],
        "confirmados": confirmados_stats["evaluados"],
        "aciertos_confirmados": confirmados_stats["aciertos"],
        "precision_confirmada": confirmados_stats["precision"],
        "por_fuente": fuente_rows,
        "por_categoria": categoria_rows,
        "generado_en": datetime.now(timezone.utc),
    }