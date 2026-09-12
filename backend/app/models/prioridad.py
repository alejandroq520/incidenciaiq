from sqlalchemy.orm import Mapped, mapped_column

from app.base_de_datos import Base


class Prioridad(Base):
    __tablename__ = "priorities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    level: Mapped[int] = mapped_column(default=1)
    color: Mapped[str] = mapped_column(default="#6B7280")
    icon: Mapped[str | None] = mapped_column(default=None)