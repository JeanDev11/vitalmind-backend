from pydantic import BaseModel
from typing import Optional


class InstrumentoRead(BaseModel):
    id_instrumento: int
    nombre: str
    descripcion: Optional[str]
    version: Optional[str]
    tipo_calificacion: str
    activo: bool

    model_config = {"from_attributes": True}
