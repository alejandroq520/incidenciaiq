"""Configuración de la aplicación cargada desde variables de entorno."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @field_validator("database_url", mode="after")
    @classmethod
    def _normalizar_driver(cls, valor: str) -> str:
        """Asegura el driver psycopg v3 aunque la URL venga sin +psycopg (Neon)."""
        if valor.startswith("postgresql://"):
            return valor.replace("postgresql://", "postgresql+psycopg://", 1)
        return valor

    app_name: str = "IncidenciaIQ"
    app_version: str = "1.2.0"
    environment: str = "development"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    api_cors_origins: str = "http://localhost:3000,http://localhost:5173"

    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/incidencia_iq"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7
    openai_timeout_seconds: float = 30.0

    log_level: str = "INFO"
    log_format: str = "text"

    sembrar_demo_data: bool = True
    sembrar_demo_incidencias: int = 130

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.openai_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()