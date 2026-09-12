"""Motor SQLAlchemy, fábrica de sesiones y base declarativa."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.configuracion import settings

engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia de FastAPI que entrega una sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()