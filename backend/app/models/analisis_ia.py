from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_de_datos import Base


class AnalisisIA(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    incidencia_id: Mapped[int] = mapped_column(
        "incident_id", ForeignKey("incidents.id", ondelete="CASCADE"), unique=True, index=True
    )
    categoria_sugerida_id: Mapped[int | None] = mapped_column(
        "suggested_category_id", ForeignKey("categories.id"), default=None
    )
    prioridad_sugerida_id: Mapped[int | None] = mapped_column(
        "suggested_priority_id", ForeignKey("priorities.id"), default=None
    )
    resumen: Mapped[str | None] = mapped_column("summary", Text, default=None)
    recomendacion: Mapped[str | None] = mapped_column("recommendation", Text, default=None)
    perspectivas: Mapped[str | None] = mapped_column("insights", Text, default=None)
    confianza: Mapped[float] = mapped_column("confidence", Float, default=0.0)
    creado_en: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), default=func.now())
    confirmado: Mapped[bool] = mapped_column("is_confirmed", Boolean, default=False)

    # Explicabilidad: cómo y por qué se produjo la sugerencia.
    fuente: Mapped[str] = mapped_column("source", String(32), default="heuristic")
    justificacion: Mapped[str | None] = mapped_column("rationale", Text, default=None)
    incidencia_referencia_id: Mapped[int | None] = mapped_column(
        "reference_incident_id", ForeignKey("incidents.id"), default=None
    )
    indice_similitud: Mapped[float | None] = mapped_column("similarity_score", Float, default=None)

    incidencia: Mapped["Incidencia"] = relationship(  # noqa: F821
        back_populates="analisis_ia", foreign_keys=[incidencia_id]
    )
    categoria_sugerida: Mapped["Categoria | None"] = relationship()  # noqa: F821
    prioridad_sugerida: Mapped["Prioridad | None"] = relationship()  # noqa: F821
    incidencia_referencia: Mapped["Incidencia | None"] = relationship(  # noqa: F821
        foreign_keys=[incidencia_referencia_id]
    )