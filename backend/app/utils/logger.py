"""Configuración del logger estructurado."""

import logging
import sys

from app.configuracion import settings

_CONFIGURED_LOGGERS: set[str] = set()


def get_logger(name: str = "incidenciaiq") -> logging.Logger:
    if name in _CONFIGURED_LOGGERS:
        return logging.getLogger(name)

    logger = logging.getLogger(name)
    if logger.handlers:
        _CONFIGURED_LOGGERS.add(name)
        return logger

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    if settings.log_format == "json":
        fmt = '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
    else:
        fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    logger.propagate = False

    _CONFIGURED_LOGGERS.add(name)
    return logger