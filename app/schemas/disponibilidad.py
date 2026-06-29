from pydantic import BaseModel, field_validator
from datetime import date, time


class DisponibilidadCreate(BaseModel):
    fecha: date
    hora_inicio: time
    hora_fin: time

    @field_validator("hora_fin")
    @classmethod
    def fin_debe_ser_posterior_a_inicio(cls, v: time, info) -> time:
        hora_inicio = info.data.get("hora_inicio")
        if hora_inicio and v <= hora_inicio:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")
        return v

    @field_validator("hora_inicio")
    @classmethod
    def dentro_de_horario_laboral(cls, v: time) -> time:
        inicio_laboral = time(8, 0)
        fin_laboral = time(17, 0)
        if not (inicio_laboral <= v < fin_laboral):
            raise ValueError("El slot debe estar dentro del horario laboral (08:00 - 17:00).")
        return v


class DisponibilidadRead(BaseModel):
    id_slot: int
    id_personal: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    disponible: bool

    model_config = {"from_attributes": True}