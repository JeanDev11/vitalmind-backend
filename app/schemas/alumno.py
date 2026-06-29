from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class AlumnoCreate(BaseModel):
    codigo_matricula: str
    dni: str
    nombre_completo: str
    email_institucional: EmailStr
    anio_ingreso: Optional[int] = None
    ciclo_actual: Optional[int] = None

    @field_validator("dni")
    @classmethod
    def dni_debe_tener_8_digitos(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 8:
            raise ValueError("El DNI debe contener exactamente 8 dígitos numéricos.")
        return v

    @field_validator("codigo_matricula")
    @classmethod
    def matricula_no_vacia(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El código de matrícula no puede estar vacío.")
        return v.strip()


class AlumnoUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    email_institucional: Optional[EmailStr] = None
    ciclo_actual: Optional[int] = None
    estado: Optional[str] = None
    # activo | inactivo | desertor | egresado


class AlumnoRead(BaseModel):
    id_alumno: int
    codigo_matricula: str
    dni: str
    nombre_completo: str
    email_institucional: str
    anio_ingreso: Optional[int]
    ciclo_actual: Optional[int]
    estado: str

    model_config = {"from_attributes": True}