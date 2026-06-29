from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TokenAccesoRead(BaseModel):
    id_token: int
    id_tamizaje: int
    id_alumno: int
    estado: str
    fecha_expiracion: datetime
    fecha_uso: Optional[datetime]

    model_config = {"from_attributes": True}


class TokenRegenerateRequest(BaseModel):
    """Solicitud de regeneración de token para un alumno dentro de un tamizaje."""
    id_tamizaje: int
    id_alumno: int