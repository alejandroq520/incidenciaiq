"""Lógica de negocio del CRUD de incidencias."""

from datetime import datetime, timezone

from sqlalchemy import Select, desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import AnalisisIA, Incidencia, HistorialIncidencia, Estado
from app.schemas.incidencia import ActualizarIncidencia, CrearIncidencia
from app.utils.errores import NotFoundError

_LIST_LOAD = (
    selectinload(Incidencia.categoria),
    selectinload(Incidencia.prioridad),
    selectinload(Incidencia.estado),
)


def _elemento_lista(incidencia: Incidencia) -> dict:
    return {
        "id": incidencia.id,
        "titulo": incidencia.titulo,
        "estado": incidencia.estado.name if incidencia.estado else "",
        "prioridad": incidencia.prioridad.name if incidencia.prioridad else "",
        "categoria": incidencia.categoria.name if incidencia.categoria else "",
        "nivel_prioridad": incidencia.prioridad.level if incidencia.prioridad else 0,
        "creado_en": incidencia.creado_en,
        "actualizado_en": incidencia.actualizado_en,
    }


def _agregar_historial(
    db: Session,
    incidencia: Incidencia,
    accion: str,
    valor_nuevo: str | None,
    cambiado_por: str,
    valor_anterior: str | None = None,
) -> None:
    db.add(
        HistorialIncidencia(
            incidencia_id=incidencia.id,
            accion=accion,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            cambiado_por=cambiado_por,
        )
    )


def a_dict_lectura(incidencia: Incidencia) -> dict:
    """Serializa un objeto ORM Incidencia en un dict compatible con LecturaIncidencia."""
    analisis = incidencia.analisis_ia or None
    return {
        "id": incidencia.id,
        "titulo": incidencia.titulo,
        "descripcion": incidencia.descripcion,
        "categoria": {
            "id": incidencia.categoria.id,
            "name": incidencia.categoria.name,
            "descripcion": incidencia.categoria.descripcion,
            "color": incidencia.categoria.color,
            "icon": incidencia.categoria.icon,
        }
        if incidencia.categoria
        else None,
        "prioridad": {
            "id": incidencia.prioridad.id,
            "name": incidencia.prioridad.name,
            "level": incidencia.prioridad.level,
            "color": incidencia.prioridad.color,
            "icon": incidencia.prioridad.icon,
        }
        if incidencia.prioridad
        else None,
        "estado": {
            "id": incidencia.estado.id,
            "name": incidencia.estado.name,
            "descripcion": incidencia.estado.descripcion,
            "color": incidencia.estado.color,
        }
        if incidencia.estado
        else None,
        "creado_en": incidencia.creado_en,
        "actualizado_en": incidencia.actualizado_en,
        "creado_por": incidencia.creado_por,
        "notas": incidencia.notas,
        "tiempo_resolucion_minutos": incidencia.tiempo_resolucion_minutos,
        "resuelto_en": incidencia.resuelto_en,
        "analisis_ia": {
            "id": analisis.id,
            "categoria_sugerida": (
                analisis.categoria_sugerida.name
                if analisis.categoria_sugerida
                else None
            ),
            "prioridad_sugerida": (
                analisis.prioridad_sugerida.name
                if analisis.prioridad_sugerida
                else None
            ),
            "resumen": analisis.resumen,
            "recomendacion": analisis.recomendacion,
            "confianza": analisis.confianza,
            "creado_en": analisis.creado_en,
            "confirmado": analisis.confirmado,
            "fuente": analisis.fuente,
            "justificacion": analisis.justificacion,
            "incidencia_referencia_id": analisis.incidencia_referencia_id,
            "indice_similitud": analisis.indice_similitud,
        }
        if analisis
        else None,
        "historial": [
            {
                "fecha": h.fecha,
                "accion": h.accion,
                "valor_anterior": h.valor_anterior,
                "valor_nuevo": h.valor_nuevo,
                "cambiado_por": h.cambiado_por,
            }
            for h in incidencia.historial
        ],
    }


def crear_incidencia(db: Session, data: CrearIncidencia) -> Incidencia:
    incidencia = Incidencia(
        titulo=data.titulo,
        descripcion=data.descripcion,
        categoria_id=data.categoria_id,
        prioridad_id=data.prioridad_id,
        estado_id=1,  # Abierta
        creado_por=data.creado_por or "Sistema Demo",
    )
    db.add(incidencia)
    db.flush()
    _agregar_historial(db, incidencia, "Creada", "Abierta", incidencia.creado_por)
    db.commit()
    db.refresh(incidencia)
    return incidencia


def aplicar_filtros(
    query: Select,
    estado_ids: list[int] | None,
    prioridad_ids: list[int] | None,
    categoria_ids: list[int] | None,
    date_from: datetime | None,
    date_to: datetime | None,
    search: str | None,
) -> Select:
    if estado_ids:
        query = query.where(Incidencia.estado_id.in_(estado_ids))
    if prioridad_ids:
        query = query.where(Incidencia.prioridad_id.in_(prioridad_ids))
    if categoria_ids:
        query = query.where(Incidencia.categoria_id.in_(categoria_ids))
    if date_from:
        query = query.where(Incidencia.creado_en >= date_from)
    if date_to:
        query = query.where(Incidencia.creado_en <= date_to)
    if search:
        pattern = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(Incidencia.titulo).like(pattern),
                func.lower(Incidencia.descripcion).like(pattern),
            )
        )
    return query


def obtener_incidencias(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    estado_ids: list[int] | None = None,
    prioridad_ids: list[int] | None = None,
    categoria_ids: list[int] | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search: str | None = None,
    sort_by: str = "creado_en",
    order: str = "desc",
) -> dict:
    base = select(Incidencia).options(*_LIST_LOAD)
    base = aplicar_filtros(
        base, estado_ids, prioridad_ids, categoria_ids, date_from, date_to, search
    )

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0

    column_map = {
        "creado_en": Incidencia.creado_en,
        "actualizado_en": Incidencia.actualizado_en,
        "prioridad": Incidencia.prioridad_id,
        "id": Incidencia.id,
        "titulo": Incidencia.titulo,
    }
    column = column_map.get(sort_by, Incidencia.creado_en)
    base = base.order_by(desc(column) if order == "desc" else column.asc())

    incidencias = db.scalars(base.offset(skip).limit(limit)).all()
    items = [_elemento_lista(i) for i in incidencias]
    return {"total": total, "skip": skip, "limit": limit, "items": items}


def obtener_incidencia_por_id(db: Session, incidencia_id: int) -> Incidencia:
    query = (
        select(Incidencia)
        .options(
            selectinload(Incidencia.categoria),
            selectinload(Incidencia.prioridad),
            selectinload(Incidencia.estado),
            selectinload(Incidencia.historial),
            selectinload(Incidencia.analisis_ia).selectinload(
                AnalisisIA.categoria_sugerida
            ),
            selectinload(Incidencia.analisis_ia).selectinload(
                AnalisisIA.prioridad_sugerida
            ),
            selectinload(Incidencia.analisis_ia).selectinload(
                AnalisisIA.incidencia_referencia
            ),
        )
        .where(Incidencia.id == incidencia_id)
    )
    incidencia = db.scalar(query)
    if incidencia is None:
        raise NotFoundError(f"Incidencia con ID {incidencia_id} no encontrada")
    return incidencia


def actualizar_incidencia(
    db: Session, incidencia_id: int, updates: ActualizarIncidencia, cambiado_por: str
) -> Incidencia:
    incidencia = obtener_incidencia_por_id(db, incidencia_id)

    if updates.estado_id is not None and updates.estado_id != incidencia.estado_id:
        old_estado = incidencia.estado.name if incidencia.estado else str(incidencia.estado_id)
        new_estado = (
            db.get(Estado, updates.estado_id).name
            if db.get(Estado, updates.estado_id)
            else str(updates.estado_id)
        )
        incidencia.estado_id = updates.estado_id
        _agregar_historial(db, incidencia, "Cambio de estado", new_estado, cambiado_por, old_estado)

    if updates.prioridad_id is not None and updates.prioridad_id != incidencia.prioridad_id:
        incidencia.prioridad_id = updates.prioridad_id
        _agregar_historial(
            db,
            incidencia,
            "Cambio de prioridad",
            str(updates.prioridad_id),
            cambiado_por,
        )

    if updates.categoria_id is not None and updates.categoria_id != incidencia.categoria_id:
        incidencia.categoria_id = updates.categoria_id
        _agregar_historial(
            db,
            incidencia,
            "Cambio de categoría",
            str(updates.categoria_id),
            cambiado_por,
        )

    if updates.notas is not None:
        incidencia.notas = updates.notas
        _agregar_historial(db, incidencia, "Notas actualizadas", "Notas", cambiado_por)

    incidencia.actualizado_en = datetime.now(timezone.utc)

    estado = db.get(Estado, incidencia.estado_id)
    if estado and estado.name.lower() == "cerrada":
        if incidencia.resuelto_en is None:
            incidencia.resuelto_en = datetime.now(timezone.utc)
        if incidencia.tiempo_resolucion_minutos is None:
            elapsed = incidencia.resuelto_en - incidencia.creado_en
            incidencia.tiempo_resolucion_minutos = max(
                0, int(elapsed.total_seconds() // 60)
            )
        _agregar_historial(
            db,
            incidencia,
            "Incidencia cerrada",
            f"{incidencia.tiempo_resolucion_minutos} min",
            cambiado_por,
        )
    elif incidencia.estado_id != 3 and incidencia.resuelto_en is not None:
        incidencia.resuelto_en = None

    db.commit()
    db.refresh(incidencia)
    return incidencia


def confirmar_analisis_ia(db: Session, incidencia_id: int, confirmado: bool) -> Incidencia:
    incidencia = obtener_incidencia_por_id(db, incidencia_id)
    if incidencia.analisis_ia:
        incidencia.analisis_ia.confirmado = confirmado
        _agregar_historial(
            db,
            incidencia,
            "Clasificación confirmada" if confirmado else "Confirmación retirada",
            "Sí" if confirmado else "No",
            "Usuario",
        )
        db.commit()
        db.refresh(incidencia)
    return incidencia