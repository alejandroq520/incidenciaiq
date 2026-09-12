"""Datos de referencia e incidencias demo realistas.

Idempotente: omite inserciones cuando las tablas de referencia ya tienen datos.
Controla la cantidad de incidencias demo mediante la variable de entorno
(se mapea al ajuste settings.sembrar_demo_incidencias).
"""

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.configuracion import settings
from app.models import Categoria, Incidencia, HistorialIncidencia, Prioridad, Estado

CATEGORIES = [
    ("Acceso", "Problemas de autenticación", "#EF4444", "lock-open"),
    ("Pagos", "Problemas de procesamiento de pagos", "#F59E0B", "credit-card"),
    ("Sistema", "Errores generales del sistema", "#3B82F6", "server"),
    ("Red", "Problemas de conectividad", "#8B5CF6", "wifi-off"),
    ("Otros", "Otros temas", "#6B7280", "help-circle"),
]

PRIORITIES = [
    ("Baja", 1, "#10B981", "arrow-down"),
    ("Media", 2, "#3B82F6", "minus"),
    ("Alta", 3, "#F97316", "arrow-up"),
    ("Crítica", 4, "#EF4444", "alert-circle"),
]

STATES = [
    ("Abierta", "Incidencia registrada", "#EF4444"),
    ("Pendiente", "Bajo investigación", "#F59E0B"),
    ("Cerrada", "Resuelta", "#10B981"),
]

TITLES = {
    "Acceso": [
        "Error de acceso al sistema",
        "Usuarios no pueden iniciar sesión",
        "Sesiones expiradas de forma intermitente",
        "Cuenta bloqueada tras varios intentos",
        "Problemas con el restablecimiento de contraseña",
        "Inicio de sesión lento en horario pico",
        "Error de doble factor en la autenticación",
    ],
    "Pagos": [
        "Pagos rechazados al procesar tarjeta",
        "Fallas en la pasarela de pagos",
        "Reembolso no procesado",
        "Error al generar factura",
        "Transacciones duplicadas detectadas",
        "Latencia en el checkout",
        "Error de cobro en suscripción",
    ],
    "Sistema": [
        "El API presenta errores 500",
        "Inestabilidad en el servidor de aplicaciones",
        "Base de datos lenta en consultas",
        "Página en blanco al cargar el dashboard",
        "Error general del sistema al guardar",
        "Proceso en segundo plano detenido",
        "Rendimiento degradado en hora punta",
    ],
    "Red": [
        "Caída de conectividad en la oficina",
        "Latencia alta en la red",
        "Problemas de DNS intermitentes",
        "Sin conexión al servicio externo",
        "Timeout en llamadas a recurso externo",
        "Pérdida de paquetes en la red",
    ],
    "Otros": [
        "Consulta de información no clasificada",
        "Aviso de mantenimiento programado",
        "Duda operativa sin categoría clara",
        "Reporte general enviado por un usuario",
    ],
}

ADEQUATE_PRIORITIES = {
    "Acceso": ("Baja", "Media", "Alta", "Crítica"),
    "Pagos": ("Baja", "Media", "Alta", "Crítica"),
    "Sistema": ("Media", "Alta", "Crítica"),
    "Red": ("Media", "Alta"),
    "Otros": ("Baja", "Media"),
}


def _ensure_reference_data(db: Session) -> None:
    if db.scalar(select(func.count(Categoria.id))) == 0:
        for name, desc, color, icon in CATEGORIES:
            db.add(Categoria(name=name, descripcion=desc, color=color, icon=icon))
    if db.scalar(select(func.count(Prioridad.id))) == 0:
        for name, level, color, icon in PRIORITIES:
            db.add(Prioridad(name=name, level=level, color=color, icon=icon))
    if db.scalar(select(func.count(Estado.id))) == 0:
        for name, desc, color in STATES:
            db.add(Estado(name=name, descripcion=desc, color=color))
    db.commit()


def _sembrar_incidencias(db: Session, count: int) -> None:
    if count <= 0:
        return
    if db.scalar(select(func.count(Incidencia.id))) > 0:
        return

    random.seed(42)
    categories = {c.name: c for c in db.scalars(select(Categoria)).all()}
    priorities = {p.name: p for p in db.scalars(select(Prioridad)).all()}
    estados = {s.name: s for s in db.scalars(select(Estado)).all()}
    now = datetime.now(timezone.utc)
    users = ["Sistema Demo", "Alejandro", "María", "Equipo IT"]

    created_desc = {
        "Acceso": "Los usuarios reportan problemas para iniciar sesión. El servicio de autenticación no responde correctamente y algunas cuentas quedan bloqueadas.",
        "Pagos": "Se detectaron errores en el procesamiento de pagos. Varias transacciones fueron rechazadas sin motivo aparente durante el período reportado.",
        "Sistema": "Se observan errores generales del sistema. La aplicación muestra mensajes de error y el rendimiento es inconsistente entre usuarios.",
        "Red": "Se reportan problemas de conectividad. La comunicación con algunos servicios se interrumpe y la latencia es inusualmente alta.",
        "Otros": "Reporte operativo recibido que requiere revisión. Se recomienda seguimiento manual para determinar el alcance del problema.",
    }

    for i in range(count):
        cat_name = random.choice(list(categories.keys()))
        titulo = random.choice(TITLES[cat_name])
        pri_name = random.choice(ADEQUATE_PRIORITIES[cat_name])
        created = now - timedelta(
            days=random.uniform(0, 30), hours=random.uniform(0, 24)
        )

        roll = random.random()
        if roll < 0.55:
            estado_name = "Cerrada"
        elif roll < 0.78:
            estado_name = "Abierta"
        else:
            estado_name = "Pendiente"

        incidencia = Incidencia(
            titulo=titulo,
            descripcion=created_desc[cat_name],
            categoria_id=categories[cat_name].id,
            prioridad_id=priorities[pri_name].id,
            estado_id=estados[estado_name].id,
            creado_en=created,
            actualizado_en=created + timedelta(hours=random.uniform(1, 6)),
            creado_por=random.choice(users),
        )

        if estado_name == "Cerrada":
            minutes = random.randint(15, 60 * 48)
            incidencia.tiempo_resolucion_minutos = minutes
            incidencia.resuelto_en = created + timedelta(minutes=minutes)
            incidencia.actualizado_en = incidencia.resuelto_en

        db.add(incidencia)
        db.flush()
        db.add(
            HistorialIncidencia(
                incidencia_id=incidencia.id,
                fecha=incidencia.creado_en,
                accion="Creada",
                valor_nuevo="Abierta",
                cambiado_por=incidencia.creado_por,
            )
        )
    db.commit()


def sembrar(db: Session) -> None:
    _ensure_reference_data(db)
    if settings.sembrar_demo_data:
        _sembrar_incidencias(db, settings.sembrar_demo_incidencias)