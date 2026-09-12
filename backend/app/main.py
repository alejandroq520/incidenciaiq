"""IncidenciaIQ - punto de entrada de la aplicación FastAPI."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.base_de_datos import Base, SessionLocal, engine
from app.configuracion import settings
from app.routers import analitica, ia, incidencias
from app.sembrar import sembrar
from app.utils.logger import get_logger

logger = get_logger("main")


def _asegurar_columnas() -> None:
    """Migración ligera e idempotente de columnas añadidas tras la creación de la tabla."""
    sentencias = [
        "ALTER TABLE ai_analyses ADD COLUMN IF NOT EXISTS source VARCHAR(32) NOT NULL DEFAULT 'heuristic'",
        "ALTER TABLE ai_analyses ADD COLUMN IF NOT EXISTS rationale TEXT",
        "ALTER TABLE ai_analyses ADD COLUMN IF NOT EXISTS reference_incident_id INTEGER REFERENCES incidents(id)",
        "ALTER TABLE ai_analyses ADD COLUMN IF NOT EXISTS similarity_score DOUBLE PRECISION",
    ]
    with engine.begin() as conn:
        for sentencia in sentencias:
            conn.execute(text(sentencia))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _asegurar_columnas()
    db = SessionLocal()
    try:
        sembrar(db)
    finally:
        db.close()
    logger.info(
        "%s v%s arrancando en modo %s",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Monitoreo inteligente de incidencias con análisis IA.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incidencias.router)
app.include_router(analitica.router)
app.include_router(ia.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


DIST_DIR = Path(__file__).resolve().parent.parent / "dist"


def _montar_frontend() -> None:
    """Sirve el frontend compilado (Vite dist/) junto a la API en una sola app."""
    if not (DIST_DIR / "index.html").is_file():
        return
    if (DIST_DIR / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        archivo = DIST_DIR / full_path
        if full_path and archivo.is_file():
            return FileResponse(archivo)
        return FileResponse(DIST_DIR / "index.html")


_montar_frontend()


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception):
    logger.exception("Excepción no controlada: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor. Intenta de nuevo más tarde."},
    )