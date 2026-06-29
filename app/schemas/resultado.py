from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ResultadoResumen(BaseModel):
    """
    Vista compacta para el panel de la psicóloga —
    listado de resultados por tamizaje.
    """
    id_resultado: int
    id_alumno: int
    nombre_alumno: str
    codigo_matricula: str
    nombre_perfil: Optional[str]
    nivel_riesgo: Optional[str]
    puntaje_emotividad: Optional[float]
    puntaje_actividad: Optional[float]
    puntaje_resonancia: Optional[float]
    alerta_emotividad_alta: str
    estado_calculo: str
    fecha_calculo: Optional[datetime]

    model_config = {"from_attributes": True}


class ResultadoRead(ResultadoResumen):
    """
    Vista completa — incluye interpretación IA.
    Se usa al abrir el perfil individual de un alumno.
    """
    id_tamizaje: int
    puntaje_total: Optional[float]
    ia_diagnostico: Optional[str]
    ia_caracteristicas: Optional[str]
    ia_recomendaciones: Optional[str]

    model_config = {"from_attributes": True}


class SolicitudInterpretacionIA(BaseModel):
    """
    Solicitud manual de generación de interpretación IA
    para perfiles de monitoreo (Colérico, Sentimental).
    """
    id_resultado: int