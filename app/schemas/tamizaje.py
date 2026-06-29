from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class TamizajeCreate(BaseModel):
    id_instrumento: int
    nombre: str
    descripcion: Optional[str] = None
    fecha_limite_respuesta: datetime

    @field_validator("fecha_limite_respuesta")
    @classmethod
    def fecha_debe_ser_futura(cls, v: datetime) -> datetime:
        if v <= datetime.now(tz=v.tzinfo):
            raise ValueError("La fecha límite de respuesta debe ser una fecha futura.")
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre del tamizaje no puede estar vacío.")
        return v.strip()


class TamizajeUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_limite_respuesta: Optional[datetime] = None
    estado: Optional[str] = None
    # borrador | activo | cerrado | anulado


class TamizajeRead(BaseModel):
    id_tamizaje: int
    id_personal_creador: int
    id_instrumento: int
    nombre: str
    descripcion: Optional[str]
    fecha_creacion: datetime
    fecha_limite_respuesta: datetime
    estado: str

    model_config = {"from_attributes": True}


class TamizajeConEstadistica(TamizajeRead):
    """Extiende TamizajeRead con contadores para el panel de la psicóloga."""
    total_invitados: int = 0
    total_respondidos: int = 0
    total_pendientes: int = 0