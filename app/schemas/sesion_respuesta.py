from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional


class OpcionResumenRead(BaseModel):
    id_opcion: int
    texto_opcion: str
    orden: int

    model_config = {"from_attributes": True}


class PreguntaResumenRead(BaseModel):
    id_pregunta: int
    orden: int
    enunciado: str
    dimension: Optional[str]
    tipo_respuesta: str
    opciones: list[OpcionResumenRead]

    model_config = {"from_attributes": True}


class SesionInicioRead(BaseModel):
    """
    Respuesta al alumno al validar su token.
    Entrega los datos mínimos para renderizar el cuestionario.
    """
    id_sesion: int
    nombre_instrumento: str
    preguntas: list[PreguntaResumenRead]

    model_config = {"from_attributes": True}


class RespuestaItemRequest(BaseModel):
    id_pregunta: int
    id_opcion_seleccionada: Optional[int] = None
    valor_texto: Optional[str] = None

    @model_validator(mode="after")
    def debe_tener_al_menos_una_respuesta(self) -> "RespuestaItemRequest":
        if self.id_opcion_seleccionada is None and not self.valor_texto:
            raise ValueError(
                "Cada respuesta debe incluir id_opcion_seleccionada o valor_texto."
            )
        return self


class RespuestaEnvioRequest(BaseModel):
    """
    Payload completo del alumno al enviar el cuestionario.
    Debe incluir una respuesta por cada pregunta del instrumento.
    """
    id_sesion: int
    respuestas: list[RespuestaItemRequest]

    @model_validator(mode="after")
    def debe_tener_respuestas(self) -> "RespuestaEnvioRequest":
        if not self.respuestas:
            raise ValueError("El envío debe contener al menos una respuesta.")
        return self


class SesionEstadoRead(BaseModel):
    id_sesion: int
    estado: str
    fecha_inicio: datetime
    fecha_envio: Optional[datetime]

    model_config = {"from_attributes": True}