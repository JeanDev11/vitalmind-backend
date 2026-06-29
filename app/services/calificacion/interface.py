from abc import ABC, abstractmethod
from app.models.sesion_respuesta import SesionRespuesta
from sqlalchemy.orm import Session


class ICalculadorPerfil(ABC):
    """
    Interfaz común para todos los calculadores de perfil.
    Cada instrumento puede tener su propia implementación.
    El backend selecciona la implementación según
    instrumento.tipo_calificacion.
    """

    @abstractmethod
    def calcular(
        self,
        sesion: SesionRespuesta,
        db: Session,
    ) -> dict:
        """
        Recibe la sesión con sus respuestas ya persistidas.
        Retorna un dict con las claves:
        {
            "puntaje_emotividad":   float | None,
            "puntaje_actividad":    float | None,
            "puntaje_resonancia":   float | None,
            "puntaje_total":        float | None,
            "id_perfil":            int   | None,
            "alerta_emotividad_alta": str,     # "true" | "false"
            "ia_diagnostico":       str  | None,
            "ia_caracteristicas":   str  | None,
            "ia_recomendaciones":   str  | None,
        }
        """
        pass