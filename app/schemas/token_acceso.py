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


class TokenAccesoConAlumnoRead(BaseModel):
    """Vista para el panel de la psicóloga — invitados de un tamizaje con datos del alumno."""
    id_token: int
    id_alumno: int
    nombre_alumno: str
    codigo_matricula: str
    estado: str
    fecha_expiracion: datetime
    fecha_uso: Optional[datetime]

    model_config = {"from_attributes": True}


class TokenRegenerateRequest(BaseModel):
    """Solicitud de regeneración de token para un alumno dentro de un tamizaje."""
    id_tamizaje: int
    id_alumno: int