from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_de_datos import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Incidencia(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column("title", unique=False, index=True)
    descripcion: Mapped[str] = mapped_column("description")
    categoria_id: Mapped[int] = mapped_column(
        "category_id", ForeignKey("categories.id"), index=True
    )
    prioridad_id: Mapped[int] = mapped_column(
        "priority_id", ForeignKey("priorities.id"), index=True
    )
    estado_id: Mapped[int] = mapped_column("state_id", ForeignKey("states.id"), index=True)
    creado_en: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), default=utcnow, index=True
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    creado_por: Mapped[str] = mapped_column("created_by", default="Sistema Demo")
    notas: Mapped[str | None] = mapped_column("notes", default=None)
    tiempo_resolucion_minutos: Mapped[int | None] = mapped_column(
        "resolution_time_minutes", default=None
    )
    resuelto_en: Mapped[datetime | None] = mapped_column(
        "resolved_at", DateTime(timezone=True), default=None
    )

    categoria: Mapped["Categoria"] = relationship()  # noqa: F821
    prioridad: Mapped["Prioridad"] = relationship()  # noqa: F821
    estado: Mapped["Estado"] = relationship()  # noqa: F821
    analisis_ia: Mapped["AnalisisIA | None"] = relationship(  # noqa: F821
        back_populates="incidencia",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="AnalisisIA.incidencia_id",
    )
    historial: Mapped[list["HistorialIncidencia"]] = relationship(  # noqa: F821
        back_populates="incidencia",
        cascade="all, delete-orphan",
        order_by="HistorialIncidencia.fecha",
    )