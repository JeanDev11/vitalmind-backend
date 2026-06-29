from sqlalchemy.orm import Session

from app.models.sesion_respuesta import SesionRespuesta
from app.models.respuesta_item import RespuestaItem
from app.models.opcion_respuesta import OpcionRespuesta
from app.models.pregunta import Pregunta
from app.models.perfil_psicologico import PerfilPsicologico
from app.services.calificacion.interface import ICalculadorPerfil

# ---------------------------------------------------------------------------
# Umbrales de la Matriz de Vicuña Peri
# E ≥ 54 → Emotivo     | E < 54 → No Emotivo
# A ≥ 52 → Activo      | A < 52 → No Activo
# R ≥ 52 → Secundario  | R < 52 → Primario
# ---------------------------------------------------------------------------
UMBRAL_EMOTIVIDAD = 54.0
UMBRAL_ACTIVIDAD  = 52.0
UMBRAL_RESONANCIA = 52.0

# Umbral de alerta por Emotividad alta (regla de negocio adicional)
UMBRAL_ALERTA_EMOTIVIDAD = 75.0


class CalculadorBergerInterno(ICalculadorPerfil):
    """
    Implementación interna del algoritmo de Gastón Berger
    según la adaptación de Luis Vicuña Peri.

    Flujo:
    1. Sumar pesos de opciones seleccionadas por dimensión.
    2. Clasificar cada dimensión contra su umbral.
    3. Buscar el perfil correspondiente en perfil_psicologico por id_instrumento.
    4. Evaluar alerta de Emotividad alta.
    """

    def calcular(self, sesion: SesionRespuesta, db: Session) -> dict:
        puntajes = self._calcular_puntajes_dimensionales(sesion, db)

        e = puntajes["emotividad"]
        a = puntajes["actividad"]
        r = puntajes["resonancia"]

        # Clasificación en ejes binarios
        es_emotivo    = e >= UMBRAL_EMOTIVIDAD
        es_activo     = a >= UMBRAL_ACTIVIDAD
        es_secundario = r >= UMBRAL_RESONANCIA

        # Buscar perfil en BD según combinación de ejes
        id_perfil = self._resolver_perfil(
            es_emotivo, es_activo, es_secundario,
            sesion.tamizaje.id_instrumento, db,
        )

        alerta = "true" if e >= UMBRAL_ALERTA_EMOTIVIDAD else "false"

        return {
            "puntaje_emotividad":    e,
            "puntaje_actividad":     a,
            "puntaje_resonancia":    r,
            "puntaje_total":         round(e + a + r, 2),
            "id_perfil":             id_perfil,
            "alerta_emotividad_alta": alerta,
            "ia_diagnostico":        None,
            "ia_caracteristicas":    None,
            "ia_recomendaciones":    None,
        }

    def _calcular_puntajes_dimensionales(
        self,
        sesion: SesionRespuesta,
        db: Session,
    ) -> dict:
        """
        Suma los valores numéricos de las opciones seleccionadas
        agrupando por dimensión de la pregunta.
        El valor ya incorpora la inversión lógica de Resonancia
        desde el seed de opcion_respuesta.
        """
        puntajes = {"emotividad": 0.0, "actividad": 0.0, "resonancia": 0.0}

        items = (
            db.query(RespuestaItem)
            .filter_by(id_sesion=sesion.id_sesion)
            .all()
        )

        for item in items:
            if item.id_opcion_seleccionada is None:
                continue

            opcion = db.query(OpcionRespuesta).filter_by(
                id_opcion=item.id_opcion_seleccionada
            ).first()

            pregunta = db.query(Pregunta).filter_by(
                id_pregunta=item.id_pregunta
            ).first()

            if opcion and pregunta and pregunta.dimension in puntajes:
                puntajes[pregunta.dimension] += float(opcion.valor_numerico)

        return {k: round(v, 2) for k, v in puntajes.items()}

    def _resolver_perfil(
        self,
        es_emotivo: bool,
        es_activo: bool,
        es_secundario: bool,
        id_instrumento: int,
        db: Session,
    ) -> int | None:
        """
        Mapea la combinación de ejes al nombre del perfil
        y lo busca en la tabla perfil_psicologico.
        """
        # Mapa de combinaciones → nombre canónico del perfil
        mapa = {
            (True,  True,  True):  "Pasional",
            (True,  True,  False): "Colérico",
            (True,  False, True):  "Sentimental",
            (True,  False, False): "Nervioso",
            (False, True,  True):  "Flemático",
            (False, True,  False): "Sanguíneo",
            (False, False, True):  "Apático",
            (False, False, False): "Amorfo",
        }
        nombre_perfil = mapa.get((es_emotivo, es_activo, es_secundario))

        if not nombre_perfil:
            return None

        perfil = db.query(PerfilPsicologico).filter_by(
            id_instrumento=id_instrumento,
            nombre_perfil=nombre_perfil,
        ).first()

        return perfil.id_perfil if perfil else None