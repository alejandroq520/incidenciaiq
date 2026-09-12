from pydantic import BaseModel


class RespuestaError(BaseModel):
    detail: str