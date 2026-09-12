"""Servicio de IA: clasificación, asistente de preguntas y perspectivas con la API de OpenAI.

Cuando OPENAI_API_KEY no está configurada (o la llamada a la API falla), se usa un
respaldo heurístico determinista para que la plataforma siga siendo totalmente
funcional en demos y desarrollo local.
"""

import json
import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.configuracion import settings
from app.models import AnalisisIA, Categoria, Incidencia, Prioridad, Estado
from app.prompts import clasificacion as clasificacion_prompt
from app.prompts import asistente as asistente_prompt
from app.prompts import analisis as analisis_prompt
from app.services.servicio_casos import buscar_caso_referencia
from app.utils.logger import get_logger

logger = get_logger("servicio_ia")

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Acceso": [
        "acceso", "login", "logue", "autentic", "sesión", "sesion",
        "contraseña", "password", "permiso", "credencial", "2fa", "token",
        "inicio de sesión", "cuenta bloqueada",
    ],
    "Pagos": [
        "pago", "pagos", "transacc", "tarjeta", "factur", "cobro",
        "checkout", "débito", "debito", "crédito", "credito", "reembolso",
        "pasarela", "pago rechazado",
    ],
    "Red": [
        "red", "conectividad", "conexión", "conexion", "latencia", "wifi",
        "internet", "dns", "timeout", "enrut", "router", "caída de red",
        "sin conexión", "paquete perdido",
    ],
    "Sistema": [
        "sistema", "crash", "error", "bug", "falla", "freeze", "congelad",
        "lento", "lentitud", "performance", "servidor", "api", "base de datos",
        "página en blanco", "no responde", "bloquea", "excepción", "500",
    ],
}

PRIORITY_KEYWORDS: dict[str, list[str]] = {
    "Crítica": [
        "crítica", "critica", "masivo", "masiva", "inoperable", "todos los usuarios",
        "generalizado", "página en blanco", "no funciona", "emergencia",
        "caída total", "producción caída", "total",
    ],
    "Alta": [
        "múltiples usu", "varios usuarios", "muchos usuarios", "significativo",
        "extendido", "afecta a", "bloquea a", "amplio", "incidencias múltiple",
    ],
    "Media": [
        "intermitente", "algunos", "parcial", "moderado", "lentitud",
        "retraso", "ocasional", "esporádico", "leve",
    ],
}

PRIORITY_ORDER = {"Crítica": 4, "Alta": 3, "Media": 2, "Baja": 1}

CONFIDENCE_KEYWORDS_HIGH = ["no funciona", "caída", "emergencia", "generalizado", "masivo"]


def _client():
    from openai import OpenAI

    return OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
    )


def _llamar_llm(system: str, user: str) -> str:
    client = _client()
    completion = client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=settings.openai_max_tokens,
        temperature=settings.openai_temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return completion.choices[0].message.content or ""


def _extraer_json(text: str) -> Any:
    cleaned = text.strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start:end])
        except json.JSONDecodeError:
            pass
    start = cleaned.find("[")
    end = cleaned.rfind("]") + 1
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start:end])
        except json.JSONDecodeError:
            pass
    raise ValueError(f"JSON no recuperable de la respuesta: {text[:200]}")


# ---------------------------------------------------------------------------
# Heuristic fallback
# ---------------------------------------------------------------------------

def _contar_palabras(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for kw in keywords if kw in lowered)


def _palabras_coincidentes(text: str, keywords: list[str]) -> list[str]:
    lowered = text.lower()
    return [kw for kw in keywords if kw in lowered]


def clasificar_heuristica(titulo: str, descripcion: str) -> dict:
    text = f"{titulo}. {descripcion}"
    lowered = text.lower()

    cat_scores = {
        name: _contar_palabras(lowered, kws) for name, kws in CATEGORY_KEYWORDS.items()
    }
    best_cat = max(cat_scores, key=cat_scores.get)
    if cat_scores[best_cat] == 0:
        best_cat = "Otros"

    pri_scores = {
        name: _contar_palabras(lowered, kws) for name, kws in PRIORITY_KEYWORDS.items()
    }
    best_pri = "Media"
    if pri_scores["Crítica"] > 0:
        best_pri = "Crítica"
    elif pri_scores["Alta"] > 0:
        best_pri = "Alta"
    elif pri_scores["Media"] > 0:
        best_pri = "Media"
    else:
        best_pri = "Baja"

    confianza = round(min(0.55 + 0.05 * max(cat_scores.values()), 0.93), 2)
    if any(kw in lowered for kw in CONFIDENCE_KEYWORDS_HIGH):
        confianza = min(confianza + 0.2, 0.97)

    resumen_map = {
        "Acceso": "Posible incidencia de autenticación que afecta el inicio de sesión de los usuarios.",
        "Pagos": "Posible incidencia en el procesamiento de pagos o transacciones.",
        "Red": "Posible problema de conectividad o infraestructura de red.",
        "Sistema": "Posible error general del sistema que impacta el funcionamiento de la aplicación.",
        "Otros": "Incidencia registrada que requiere revisión manual para su clasificación.",
    }
    recomendacion_map = {
        "Acceso": "Revisar el servicio de autenticación y los registros de acceso de los últimos 30 minutos.",
        "Pagos": "Verificar la pasarela de pagos y las transacciones recientes.",
        "Red": "Revisar infraestructura de red y logs de conectividad.",
        "Sistema": "Revisar logs del servidor y el estado de los servicios afectados.",
        "Otros": "Asignar a un analista para revisión manual y clasificación.",
    }
    return {
        "categoria_sugerida": best_cat,
        "prioridad_sugerida": best_pri,
        "resumen": resumen_map[best_cat],
        "recomendacion": recomendacion_map[best_cat],
        "confianza": confianza,
        "fuente": "heuristic",
        "evidence": {
            name: _palabras_coincidentes(lowered, kws)
            for name, kws in CATEGORY_KEYWORDS.items()
            if _palabras_coincidentes(lowered, kws)
        },
    }


def _categoria_por_nombre(db: Session, name: str) -> Categoria | None:
    return db.scalar(select(Categoria).where(func.lower(Categoria.name) == name.lower()))


def _prioridad_por_nombre(db: Session, name: str) -> Prioridad | None:
    return db.scalar(select(Prioridad).where(func.lower(Prioridad.name) == name.lower()))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _construir_justificacion(
    fuente: str,
    evidence: dict[str, list[str]] | None,
    ref_incidencia: Incidencia | None,
    similarity: float,
    categoria: str | None,
) -> str:
    parts: list[str] = []
    if fuente in ("heuristic", "heuristic_case") and evidence:
        matched = [kw for group in evidence.values() for kw in group]
        if matched:
            parts.append(
                f"Clasificación por reglas: coincidieron las palabras clave "
                f"({', '.join(sorted(set(matched))[:8])})."
            )
    if "openai" in fuente:
        parts.append(
            f"Clasificación generada por el modelo {settings.openai_model.split('-', 1)[0]} "
            f"{settings.openai_model}."
        )
    if ref_incidencia is not None:
        parts.append(
            f"Respaldada por el caso histórico INC-{ref_incidencia.id} ({categoria or 'Otros'}), "
            f"con {round(similarity * 100)}% de similitud de texto."
        )
    return " ".join(parts) if parts else "Sin justificación detallada."


def clasificar_incidencia(db: Session, incidencia: Incidencia) -> dict | None:
    """Clasifica una incidencia, persiste el análisis y devuelve el dict de datos.

    La sugerencia siempre está fundamentada: combina, cuando está disponible, el
    modelo GPT, el clasificador determinista por reglas y un caso histórico real
    (TF-IDF + coseno). "fuente" registra exactamente cuál de ellos produjo la
    respuesta, de modo que el origen nunca queda oculto.

    Best-effort: nunca lanza excepciones; devuelve None si falla para que la
    creación de incidencias nunca se vea bloqueada por la capa de IA.
    """
    try:
        similarity, ref_incidencia, ref_categoria = buscar_caso_referencia(
            db, incidencia.titulo, incidencia.descripcion, incidencia.id
        )

        result: dict | None = None
        evidence: dict[str, list[str]] | None = None
        if settings.llm_enabled:
            try:
                system, user = clasificacion_prompt.build_prompt(
                    incidencia.titulo, incidencia.descripcion
                )
                raw = _llamar_llm(system, user)
                result = _extraer_json(raw)
            except Exception:
                logger.exception("La clasificación con OpenAI falló; usando respaldo")
                result = None

        if result is None:
            evidence = clasificar_heuristica(incidencia.titulo, incidencia.descripcion)
            if evidence.get("categoria_sugerida") == "Otros" and ref_categoria:
                result = {
                    "categoria_sugerida": ref_categoria,
                    "prioridad_sugerida": "Media",
                    "resumen": (
                        f"Se identificó similitud con la incidencia INC-{ref_incidencia.id} "
                        f"resuelta en la categoría {ref_categoria}."
                    ),
                    "recomendacion": (
                        f"Revisar el caso histórico INC-{ref_incidencia.id} como referencia "
                        f"de resolución."
                    ),
                    "confianza": round(min(similarity + 0.25, 0.9), 2),
                }
                fuente = "case"
            else:
                fuente = "heuristic"
                result = {
                    "categoria_sugerida": evidence["categoria_sugerida"],
                    "prioridad_sugerida": evidence["prioridad_sugerida"],
                    "resumen": evidence["resumen"],
                    "recomendacion": evidence["recomendacion"],
                    "confianza": evidence["confianza"],
                }
        elif ref_incidencia is not None:
            fuente = "openai_case"
            base_conf = float(result.get("confianza", 0.7) or 0.7)
            result["confianza"] = round(0.6 * base_conf + 0.4 * similarity, 2)
        else:
            fuente = "openai"

        categoria = _categoria_por_nombre(db, result.get("categoria_sugerida", ""))
        prioridad = _prioridad_por_nombre(db, result.get("prioridad_sugerida", ""))

        analisis = AnalisisIA(
            incidencia_id=incidencia.id,
            categoria_sugerida_id=categoria.id if categoria else None,
            prioridad_sugerida_id=prioridad.id if prioridad else None,
            resumen=result.get("resumen") or "",
            recomendacion=result.get("recomendacion") or "",
            confianza=float(result.get("confianza", 0.5) or 0.5),
            fuente=fuente,
            justificacion=_construir_justificacion(
                fuente,
                evidence if fuente in ("heuristic", "heuristic_case") else None,
                ref_incidencia,
                similarity,
                ref_categoria,
            ),
            incidencia_referencia_id=ref_incidencia.id if ref_incidencia else None,
            indice_similitud=round(similarity, 4) if ref_incidencia else None,
        )
        db.add(analisis)
        db.commit()
        db.refresh(analisis)

        return {
            "id": analisis.id,
            "categoria_sugerida": result.get("categoria_sugerida") or "Otros",
            "prioridad_sugerida": result.get("prioridad_sugerida") or "Media",
            "resumen": analisis.resumen,
            "recomendacion": analisis.recomendacion,
            "confianza": analisis.confianza,
            "creado_en": analisis.creado_en,
            "confirmado": False,
            "fuente": fuente,
            "justificacion": analisis.justificacion,
            "incidencia_referencia_id": analisis.incidencia_referencia_id,
            "indice_similitud": analisis.indice_similitud,
        }
    except Exception:
        logger.exception("La clasificación IA falló")
        return None


def _mapa_id_estados(db: Session) -> dict[str, int]:
    estados = db.scalars(select(Estado)).all()
    return {s.name.lower(): s.id for s in estados}


def _id_prioridades_criticas(db: Session) -> list[int]:
    rows = db.scalars(
        select(Prioridad).where(func.lower(Prioridad.name) == "crítica")
    ).all()
    if not rows:
        rows = db.scalars(
            select(Prioridad).order_by(Prioridad.level.desc()).limit(1)
        ).all()
    return [r.id for r in rows]


def _armar_contexto(db: Session) -> dict:
    estado_ids = _mapa_id_estados(db)
    closed_ids = [sid for name, sid in estado_ids.items() if name == "cerrada"]
    open_ids = [sid for name, sid in estado_ids.items() if name == "abierta"]
    pending_ids = [sid for name, sid in estado_ids.items() if name == "pendiente"]
    critical_ids = _id_prioridades_criticas(db)

    total = db.scalar(select(func.count()).select_from(Incidencia)) or 0
    critical = (
        db.scalar(
            select(func.count())
            .select_from(Incidencia)
            .where(Incidencia.prioridad_id.in_(critical_ids))
        )
        or 0
    )
    open_count = (
        db.scalar(
            select(func.count()).select_from(Incidencia).where(Incidencia.estado_id.in_(open_ids))
        )
        or 0
    )
    pending = (
        db.scalar(
            select(func.count()).select_from(Incidencia).where(Incidencia.estado_id.in_(pending_ids))
        )
        or 0
    )
    closed = (
        db.scalar(
            select(func.count()).select_from(Incidencia).where(Incidencia.estado_id.in_(closed_ids))
        )
        or 0
    )

    avg_minutes = db.scalar(
        select(func.avg(Incidencia.tiempo_resolucion_minutos)).where(
            Incidencia.tiempo_resolucion_minutos.is_not(None)
        )
    )
    avg_hours = round((avg_minutes or 0) / 60, 2)

    cat_rows = db.execute(
        select(Categoria.name, func.count(Incidencia.id))
        .join(Incidencia, Incidencia.categoria_id == Categoria.id)
        .group_by(Categoria.name)
        .order_by(func.count(Incidencia.id).desc())
    ).all()
    categories_breakdown = "\n".join(f"- {name}: {count}" for name, count in cat_rows)

    recent = db.scalars(
        select(Incidencia)
        .order_by(Incidencia.creado_en.desc())
        .limit(10)
        .options(selectinload(Incidencia.categoria), selectinload(Incidencia.prioridad))
    ).all()
    recent_list = "\n".join(
        f"- INC-{i.id} [{i.estado.name}] {i.titulo} (categoría: {i.categoria.name}, prioridad: {i.prioridad.name})"
        for i in recent
    )

    critical_by_cat: dict[str, int] = {}
    for identified in db.scalars(
        select(Incidencia)
        .where(Incidencia.prioridad_id.in_(critical_ids))
        .options(selectinload(Incidencia.categoria))
    ).all():
        name = identified.categoria.name if identified.categoria else "Otros"
        critical_by_cat[name] = critical_by_cat.get(name, 0) + 1

    return {
        "total_incidencias": total,
        "open_incidencias": open_count,
        "pending_incidencias": pending,
        "closed_incidencias": closed,
        "critical_incidencias": critical,
        "avg_resolution_time": avg_hours,
        "categories_breakdown": categories_breakdown or "(sin datos)",
        "recent_incidencias_list": recent_list or "(sin incidencias)",
        "critical_por_categoria": critical_by_cat,
    }


def responder_pregunta(db: Session, pregunta: str) -> dict:
    context = _armar_contexto(db)
    try:
        if settings.llm_enabled:
            try:
                system, user = asistente_prompt.build_prompt(context, pregunta)
                raw = _llamar_llm(system, user)
                respuesta = raw.strip()
            except Exception:
                logger.exception("El asistente falló; usando respuesta plantilla")
                respuesta = _respuesta_plantilla(context, pregunta)
        else:
            respuesta = _respuesta_plantilla(context, pregunta)
    except Exception:
        logger.exception("No se pudo generar la respuesta del asistente")
        respuesta = (
            "No pude procesar la pregunta en este momento. "
            "Verifica que la integración con la API de IA esté configurada."
        )

    return {
        "pregunta": pregunta,
        "respuesta": respuesta,
        "context": {
            "total_criticas": context["critical_incidencias"],
            "por_categoria": context["critical_por_categoria"],
        },
        "generado_en": datetime.now(timezone.utc),
    }


def _respuesta_plantilla(ctx: dict, pregunta: str) -> str:
    lowered = pregunta.lower()
    if "crítica" in lowered or "critica" in lowered or "críticas" in lowered:
        by_cat = ", ".join(
            f"{k} ({v})" for k, v in ctx["critical_por_categoria"].items()
        )
        return (
            f"Actualmente existen {ctx['critical_incidencias']} incidencias críticas abiertas. "
            f"Desglose por categoría: {by_cat or 'sin datos'}."
        )
    if "categoría" in lowered or "categoria" in lowered or "más incidencias" in lowered:
        lines = ctx["categories_breakdown"].splitlines()
        return (
            f"La categoría con más incidencias es: {lines[0].replace('- ', '')}." 
            if lines
            else "No hay datos de categorías disponibles."
        )
    if "promedio" in lowered or "tiempo de resolución" in lowered or "resolución" in lowered:
        return (
            f"El tiempo promedio de resolución es de {ctx['avg_resolution_time']} horas "
            f"(sobre {ctx['closed_incidencias']} incidencias cerradas)."
        )
    if "esta semana" in lowered or "semana" in lowered or "resumen" in lowered or "resume" in lowered:
        return (
            f"Resumen del sistema: {ctx['total_incidencias']} incidencias totales, "
            f"{ctx['open_incidencias']} abiertas, {ctx['pending_incidencias']} pendientes y "
            f"{ctx['closed_incidencias']} cerradas. Hay {ctx['critical_incidencias']} críticas. "
            f"El tiempo promedio de resolución es {ctx['avg_resolution_time']}h."
        )
    return (
        f"El sistema tiene {ctx['total_incidencias']} incidencias registradas: "
        f"{ctx['open_incidencias']} abiertas, {ctx['pending_incidencias']} pendientes y "
        f"{ctx['closed_incidencias']} cerradas. "
        f"Hazme preguntas más específicas (por ejemplo, sobre críticas, categorías o tiempos de resolución)."
    )


def generar_perspectivas(db: Session, period: str = "7d") -> list[dict]:
    now = datetime.now(timezone.utc)
    from app.services.servicio_analitica import (
        obtener_por_categoria,
        obtener_comparacion_categorias,
        obtener_metricas,
        obtener_tiempos_resolucion,
    )

    try:
        metrics = obtener_metricas(db, period)
        by_cat = obtener_por_categoria(db, period)
        resolution = obtener_tiempos_resolucion(db, period)
        deltas = obtener_comparacion_categorias(db, period)

        def fmt_change(value):
            if value is None:
                return "sin dato previo (sin canal de comparación)"
            return f"{value:+.1f}%"

        def fmt_delta(d: dict) -> str:
            cur, prev = d["current"], d["previous"]
            if prev <= 2:
                if prev == 0:
                    return f"nueva en el período (sin base previa)"
                return f"{cur} vs {prev} (base mínima: sin % confiable)"
            return f"{cur} vs {prev} ({fmt_change(d['delta_pct'])})"

        metrics_str = (
            f"Total: {metrics['total_incidencias']}, Abiertas: {metrics['opened_incidencias']}, "
            f"Cerradas: {metrics['closed_incidencias']}, Críticas: {metrics['critical_incidencias']}, "
            f"SLA: {metrics['sla_compliance_percentage']}%"
        )
        comparison_str = (
            f"Total vs periodo anterior: {fmt_change(metrics['comparison']['total_incidencias_change_percent'])}, "
            f"Tiempo de resolución: {metrics['comparison']['resolution_time_change_minutes']} min respecto al anterior."
        )
        categoria_str = ", ".join(
            f"{c['name']}: {c['total']}" for c in by_cat["categorias"] if c["total"]
        )
        delta_str = ", ".join(
            fmt_delta(d)
            for d in deltas
            if d["current"] > 0 or d["previous"] > 0
        )
        resolution_str = (
            f"Promedio: {resolution['average_hours']}h, Mediana: {resolution['median_hours']}h, "
            f"P95: {resolution['p95_hours']}h"
        )
        context = {
            "metrics_data": metrics_str,
            "comparison_data": comparison_str,
            "categoria_breakdown": categoria_str,
            "categoria_deltas_vs_previous_period": delta_str or "(sin datos comparables)",
            "resolution_trend": resolution_str,
        }

        if settings.llm_enabled:
            try:
                system, user = analisis_prompt.build_prompt(period, context)
                raw = _llamar_llm(system, user)
                parsed = _extraer_json(raw)
                if isinstance(parsed, list):
                    return _finalizar_perspectivas(parsed)
            except Exception:
                logger.exception("La generación de perspectivas con OpenAI falló; usando plantilla")
    except Exception:
        logger.exception("La generación de perspectivas falló")

    fallback = _perspectivas_fallback(db, period)
    return _finalizar_perspectivas(fallback)


def _finalizar_perspectivas(items: list[dict]) -> list[dict]:
    results = []
    for idx, item in enumerate(items, start=1):
        impact = item.get("impact", "medium")
        results.append(
            {
                "id": idx,
                "titulo": item.get("titulo") or "Perspectiva operativa",
                "descripcion": item.get("descripcion") or "",
                "impact": impact,
                "categoria": item.get("categoria"),
                "generado_en": datetime.now(timezone.utc),
            }
        )
    return results


def _perspectivas_fallback(db: Session, period: str) -> list[dict]:
    try:
        from app.services.servicio_analitica import obtener_por_categoria, obtener_comparacion_categorias

        by_cat = obtener_por_categoria(db, period)
        deltas = obtener_comparacion_categorias(db, period)
        top = by_cat["categorias"][0] if by_cat["categorias"] else None
        perspectivas: list[dict] = []

        increases = [
            d for d in deltas
            if d["current"] >= 3
            and d["previous"] >= 3
            and (d["delta_pct"] is not None and d["delta_pct"] >= 20)
        ]
        for d in increases:
            perspectivas.append(
                {
                    "titulo": f"{d['categoria']} aumentó {d['delta_pct']:+.0f}%",
                    "descripcion": (
                        f"La categoría {d['categoria']} pasó de {d['previous']} a "
                        f"{d['current']} incidencias respecto al periodo anterior "
                        f"(variación real de {d['delta_pct']:+.1f}%)."
                    ),
                    "impact": "high" if d["delta_pct"] >= 50 else "medium",
                    "categoria": d["categoria"],
                }
            )
        if not increases and top and top["total"] > 0:
            perspectivas.append(
                {
                    "titulo": f"Mayor actividad en {top['name']}",
                    "descripcion": (
                        f"La categoría {top['name']} concentra {top['total']} incidencias "
                        f"({top['percentage']}% del total) durante el período seleccionado."
                    ),
                    "impact": "high" if top["percentage"] >= 30 else "medium",
                    "categoria": top["name"],
                }
            )

        resolutions = [
            d for d in deltas
            if d["previous"] >= 3 and d["delta_pct"] is not None and d["delta_pct"] <= -20
        ]
        for d in resolutions:
            perspectivas.append(
                {
                    "titulo": f"{d['categoria']} bajó {abs(d['delta_pct']):+.0f}%".replace("+", ""),
                    "descripcion": (
                        f"La categoría {d['categoria']} redujo sus incidencias de "
                        f"{d['previous']} a {d['current']} respecto al periodo anterior "
                        f"(variación real de {d['delta_pct']:+.1f}%)."
                    ),
                    "impact": "positive",
                    "categoria": d["categoria"],
                }
            )

        estado_dist = db.execute(
            select(Estado.name, func.count(Incidencia.id))
            .join(Incidencia, Incidencia.estado_id == Estado.id)
            .group_by(Estado.name)
            .order_by(func.count(Incidencia.id).desc())
        ).all()
        for name, count in estado_dist:
            if name.lower() == "abierta":
                perspectivas.append(
                    {
                        "titulo": f"{count} incidencias siguen abiertas",
                        "descripcion": (
                            f"Quedan {count} incidencias abiertas sin resolver. "
                            "Se recomienda priorizar su atención según categoría."
                        ),
                        "impact": "medium",
                        "categoria": "Operación",
                    }
                )
            break
        return perspectivas[:4] or [
            {
                "titulo": "Operación estable",
                "descripcion": "No se detectaron patrones anómalos relevantes en el período analizado.",
                "impact": "positive",
                "categoria": "Operación",
            }
        ]
    except Exception:
        return [
            {
                "titulo": "Datos disponibles",
                "descripcion": "Analiza el dashboard para obtener información operativa del período.",
                "impact": "positive",
                "categoria": "Operación",
            }
        ]