from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_de_datos import Base


class HistorialIncidencia(Base):
    __tablename__ = "incident_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    incidencia_id: Mapped[int] = mapped_column(
        "incident_id", ForeignKey("incidents.id", ondelete="CASCADE"), index=True
    )
    fecha: Mapped[datetime] = mapped_column(
        "timestamp", DateTime(timezone=True), default=func.now()
    )
    accion: Mapped[str] = mapped_column("action")
    valor_anterior: Mapped[str | None] = mapped_column("old_value", default=None)
    valor_nuevo: Mapped[str | None] = mapped_column("new_value", default=None)
    cambiado_por: Mapped[str] = mapped_column("changed_by", default="Sistema Demo")

    incidencia: Mapped["Incidencia"] = relationship(back_populates="historial")  # noqa: F821