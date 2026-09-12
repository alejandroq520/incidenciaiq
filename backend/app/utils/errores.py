"""Tipos de excepción personalizados y ayudantes de error compartidos."""

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class AIProviderError(HTTPException):
    def __init__(self, detail: str = "No se pudo procesar la solicitud de IA."):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class RateLimitError(HTTPException):
    def __init__(self, detail: str = "Demasiadas solicitudes. Intenta de nuevo más tarde."):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)