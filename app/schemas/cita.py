from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CitaCreate(BaseModel):
    id_slot: int
    id_alumno: int
    id_resultado_origen: Optional[int] = None  # Nullable — cubre demanda espontánea
    motivo: Optional[str] = None


class CitaUpdate(BaseModel):
    estado: Optional[str] = None
    # programada | completada | cancelada | no_asistio
    notas_sesion: Optional[str] = None


class CitaRead(BaseModel):
    id_cita: int
    id_slot: int
    id_alumno: int
    nombre_alumno: str
    id_personal: int
    id_resultado_origen: Optional[int]
    motivo: Optional[str]
    estado: str
    notas_sesion: Optional[str]
    fecha_creacion: datetime

    model_config = {"from_attributes": True}