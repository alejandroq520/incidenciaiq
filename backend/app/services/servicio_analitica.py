"""Lógica de negocio para métricas y analítica."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Categoria, Incidencia, Prioridad, Estado

SLA_TARGET_MINUTES = 480  # 8 hours


def _id_prioridades_criticas(db: Session) -> list[int]:
    rows = db.scalars(
        select(Prioridad).where(func.lower(Prioridad.name) == "crítica")
    ).all()
    if not rows:
        rows = db.scalars(
            select(Prioridad).order_by(Prioridad.level.desc()).limit(1)
        ).all()
    return [r.id for r in rows]


def _id_estados_cerrados(db: Session) -> list[int]:
    rows = db.scalars(select(Estado).where(func.lower(Estado.name) == "cerrada")).all()
    return [r.id for r in rows]


def resolver_periodo(
    period: str = "7d",
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[datetime, datetime, str]:
    """Devuelve (inicio, fin, etiqueta) para un período dado."""
    now = datetime.now(timezone.utc)
    if period == "custom" and date_from and date_to:
        end = date_to
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        start = date_from
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        return start, end, "custom"

    if period == "30d":
        return now - timedelta(days=30), now, "30d"
    if period == "90d":
        return now - timedelta(days=90), now, "90d"
    return now - timedelta(days=7), now, "7d"


def _range_days(start: datetime, end: datetime) -> float:
    return max((end - start).total_seconds() / 86400.0, 0.1)


def obtener_metricas(
    db: Session,
    period: str = "7d",
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:
    start, end, label = resolver_periodo(period, date_from, date_to)
    closed_ids = _id_estados_cerrados(db)
    critical_ids = _id_prioridades_criticas(db)

    def snapshot(lo: datetime, hi: datetime) -> dict:
        crit = [Incidencia.creado_en >= lo, Incidencia.creado_en <= hi]
        total = db.scalar(
            select(func.count()).select_from(Incidencia).where(*crit)
        ) or 0
        opened = db.scalar(
            select(func.count())
            .select_from(Incidencia)
            .where(*crit, Incidencia.estado_id.notin_(closed_ids))
        ) or 0
        closed = db.scalar(
            select(func.count())
            .select_from(Incidencia)
            .where(*crit, Incidencia.estado_id.in_(closed_ids))
        ) or 0
        critical = db.scalar(
            select(func.count())
            .select_from(Incidencia)
            .where(*crit, Incidencia.prioridad_id.in_(critical_ids))
        ) or 0
        return {"total": total, "opened": opened, "closed": closed, "critical": critical}

    current = snapshot(start, end)
    span = _range_days(start, end)
    prev_end = start
    prev_start = prev_end - timedelta(days=span)
    previous = snapshot(prev_start, prev_end)

    def pct_change(cur: int, prev: int) -> float | None:
        if prev == 0:
            return None if cur else 0.0
        return round(((cur - prev) / prev) * 100, 1)

    closed_incidencias = db.scalars(
        select(Incidencia)
        .where(
            Incidencia.estado_id.in_(closed_ids),
            Incidencia.creado_en >= start,
            Incidencia.creado_en <= end,
            Incidencia.tiempo_resolucion_minutos.is_not(None),
        )
        .options(selectinload(Incidencia.prioridad))
    ).all()

    resolution_times = [
        i.tiempo_resolucion_minutos for i in closed_incidencias if i.tiempo_resolucion_minutos
    ]
    avg_minutes = (
        sum(resolution_times) / len(resolution_times) if resolution_times else 0
    )

    sla_ok = sum(1 for rt in resolution_times if rt <= SLA_TARGET_MINUTES)
    sla_pct = round((sla_ok / len(resolution_times)) * 100, 1) if resolution_times else 100.0

    prev_times = db.scalars(
        select(Incidencia.tiempo_resolucion_minutos).where(
            Incidencia.estado_id.in_(closed_ids),
            Incidencia.creado_en >= prev_start,
            Incidencia.creado_en <= prev_end,
            Incidencia.tiempo_resolucion_minutos.is_not(None),
        )
    ).all()
    prev_avg = (
        sum(prev_times) / len(prev_times) if prev_times else 0
    )

    recurrent_cats = db.execute(
        select(Incidencia.categoria_id, func.count())
        .where(Incidencia.creado_en >= start, Incidencia.creado_en <= end)
        .group_by(Incidencia.categoria_id)
        .having(func.count() >= 3)
    ).all()
    recurring = len(recurrent_cats)

    avg_hours = round(avg_minutes / 60, 2) if avg_minutes else 0.0
    return {
        "period": label,
        "date_from": start,
        "date_to": end,
        "total_incidencias": current["total"],
        "opened_incidencias": current["opened"],
        "closed_incidencias": current["closed"],
        "critical_incidencias": current["critical"],
        "average_resolution_time_hours": avg_hours,
        "sla_compliance_percentage": sla_pct,
        "recurring_patterns": recurring,
        "comparison": {
            "total_incidencias_change_percent": pct_change(
                current["total"], previous["total"]
            ),
            "opened_incidencias_change_percent": pct_change(
                current["opened"], previous["opened"]
            ),
            "closed_incidencias_trend": (
                "up" if current["closed"] >= previous["closed"] else "down"
            ),
            "resolution_time_trend": (
                "down"
                if (previous and prev_avg > 0 and avg_minutes <= prev_avg)
                else "up"
            ),
            "resolution_time_change_minutes": round(avg_minutes - prev_avg, 0),
            "previous_total": previous["total"],
        },
    }


def obtener_por_categoria(
    db: Session,
    period: str = "7d",
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:
    start, end, label = resolver_periodo(period, date_from, date_to)
    closed_ids = _id_estados_cerrados(db)

    rows = db.execute(
        select(Incidencia.categoria_id, Incidencia.estado_id, func.count())
        .where(Incidencia.creado_en >= start, Incidencia.creado_en <= end)
        .group_by(Incidencia.categoria_id, Incidencia.estado_id)
    ).all()

    totals: defaultdict[int, int] = defaultdict(int)
    opened_count: defaultdict[int, int] = defaultdict(int)
    closed_count: defaultdict[int, int] = defaultdict(int)

    for cat_id, estado_id, count in rows:
        totals[cat_id] += count
        if estado_id in closed_ids:
            closed_count[cat_id] += count
        else:
            opened_count[cat_id] += count

    grand = max(sum(totals.values()), 1)
    categories = db.scalars(select(Categoria).order_by(Categoria.id)).all()
    items = []
    for cat in categories:
        t = totals.get(cat.id, 0)
        items.append(
            {
                "id": cat.id,
                "name": cat.name,
                "total": t,
                "opened": opened_count.get(cat.id, 0),
                "closed": closed_count.get(cat.id, 0),
                "percentage": round((t / grand) * 100, 1),
                "color": cat.color,
            }
        )
    items.sort(key=lambda r: r["total"], reverse=True)
    return {"period": label, "categorias": items}


def obtener_tendencia(
    db: Session,
    period: str = "7d",
    granularity: str = "daily",
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:
    start, end, label = resolver_periodo(period, date_from, date_to)
    closed_ids = _id_estados_cerrados(db)

    bucket: str = "hour" if granularity == "hourly" else "day"

    created_rows = db.execute(
        select(
            func.date_trunc(bucket, Incidencia.creado_en).label("bucket"),
            func.count().label("count"),
        )
        .where(Incidencia.creado_en >= start, Incidencia.creado_en <= end)
        .group_by("bucket")
        .order_by("bucket")
    ).all()

    closed_rows = db.execute(
        select(
            func.date_trunc("day", Incidencia.creado_en).label("bucket"),
            func.count().label("count"),
        )
        .where(
            Incidencia.creado_en >= start,
            Incidencia.creado_en <= end,
            Incidencia.estado_id.in_(closed_ids),
        )
        .group_by("bucket")
        .order_by("bucket")
    ).all()

    opened_rows = db.execute(
        select(
            func.date_trunc(bucket, Incidencia.creado_en).label("bucket"),
            func.count().label("count"),
        )
        .where(
            Incidencia.creado_en >= start,
            Incidencia.creado_en <= end,
            Incidencia.estado_id.notin_(closed_ids),
        )
        .group_by("bucket")
        .order_by("bucket")
    ).all()

    def key(value) -> str:
        return value.isoformat()

    created_map = {key(r[0]): r[1] for r in created_rows}
    closed_map = {key(r[0]): r[1] for r in closed_rows}
    opened_map = {key(r[0]): r[1] for r in opened_rows}

    all_keys = sorted(set(created_map) | set(closed_map) | set(opened_map))
    data = [
        {
            "date": k if granularity == "hourly" else k[:10],
            "created": created_map.get(k, 0),
            "closed": closed_map.get(k, 0),
            "opened": opened_map.get(k, 0),
        }
        for k in all_keys
    ]
    return {"period": label, "granularity": granularity, "data": data}


def obtener_tiempos_resolucion(
    db: Session,
    period: str = "7d",
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:
    start, end, label = resolver_periodo(period, date_from, date_to)
    closed_ids = _id_estados_cerrados(db)

    incidencias = db.scalars(
        select(Incidencia)
        .where(
            Incidencia.estado_id.in_(closed_ids),
            Incidencia.creado_en >= start,
            Incidencia.creado_en <= end,
            Incidencia.tiempo_resolucion_minutos.is_not(None),
        )
        .options(selectinload(Incidencia.categoria), selectinload(Incidencia.prioridad))
    ).all()

    times = sorted(i.tiempo_resolucion_minutos for i in incidencias)
    if not times:
        return {
            "period": label,
            "average_hours": 0.0,
            "median_hours": 0.0,
            "min_hours": 0.0,
            "max_hours": 0.0,
            "p95_hours": 0.0,
            "por_categoria": [],
            "por_prioridad": [],
        }

    avg = sum(times) / len(times)
    mid = len(times) // 2
    median = (
        times[mid]
        if len(times) % 2 == 1
        else (times[mid - 1] + times[mid]) / 2
    )
    p95_idx = max(0, int(len(times) * 0.95) - 1)

    hours = lambda m: round(m / 60, 2)

    cat_agg: defaultdict[str, list[int]] = defaultdict(list)
    for i in incidencias:
        if i.categoria:
            cat_agg[i.categoria.name].append(i.tiempo_resolucion_minutos)
    por_categoria = [
        {"categoria": name, "average_hours": hours(sum(v) / len(v))}
        for name, v in cat_agg.items()
    ]
    por_categoria.sort(key=lambda r: r["average_hours"])

    pri_agg: defaultdict[str, list[int]] = defaultdict(list)
    for i in incidencias:
        if i.prioridad:
            pri_agg[i.prioridad.name].append(i.tiempo_resolucion_minutos)
    por_prioridad = [
        {"prioridad": name, "average_hours": hours(sum(v) / len(v))}
        for name, v in pri_agg.items()
    ]
    por_prioridad.sort(key=lambda r: r["average_hours"])

    return {
        "period": label,
        "average_hours": hours(avg),
        "median_hours": hours(median),
        "min_hours": hours(times[0]),
        "max_hours": hours(times[-1]),
        "p95_hours": hours(times[p95_idx]),
        "por_categoria": por_categoria,
        "por_prioridad": por_prioridad,
    }


def obtener_comparacion_categorias(
    db: Session,
    period: str = "7d",
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[dict]:
    """Cambio real por categoría frente a la ventana previa equivalente.

    delta_pct es None cuando la ventana previa no tuvo incidencias para esa
    categoría (cambio indefinido, evita valores engañosos como +13400%).
    """
    start, end, _ = resolver_periodo(period, date_from, date_to)
    span = _range_days(start, end)
    prev_end, prev_start = start, start - timedelta(days=span)

    def counts(lo: datetime, hi: datetime) -> dict[int, int]:
        rows = db.execute(
            select(Incidencia.categoria_id, func.count())
            .where(Incidencia.creado_en >= lo, Incidencia.creado_en <= hi)
            .group_by(Incidencia.categoria_id)
        ).all()
        return {cat_id: n for cat_id, n in rows}

    current = counts(start, end)
    previous = counts(prev_start, prev_end)

    categories = db.scalars(select(Categoria).order_by(Categoria.id)).all()
    result = []
    for cat in categories:
        cur = current.get(cat.id, 0)
        prev = previous.get(cat.id, 0)
        delta_pct: float | None
        if prev == 0:
            delta_pct = None
        else:
            delta_pct = round(((cur - prev) / prev) * 100, 1)
        result.append(
            {
                "categoria": cat.name,
                "current": cur,
                "previous": prev,
                "delta_pct": delta_pct,
                "is_new": cur > 0 and prev == 0,
            }
        )
    return result