from sqlalchemy.orm import Mapped, mapped_column

from app.base_de_datos import Base


class Estado(Base):
    __tablename__ = "states"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    descripcion: Mapped[str | None] = mapped_column("description", default=None)
    color: Mapped[str] = mapped_column(default="#6B7280")