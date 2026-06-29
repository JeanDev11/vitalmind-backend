import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.sesion_respuesta import SesionRespuesta
from app.models.perfil_psicologico import PerfilPsicologico
from app.services.calificacion.interface import ICalculadorPerfil
from app.services.calificacion.berger import CalculadorBergerInterno

settings = get_settings()

client = genai.Client(api_key=settings.gemini_api_key)
MODEL_NAME = "gemini-1.5-flash"

# Definimos la estructura exacta que DEBE retornar la IA
class InformePsicologico(BaseModel):
    diagnostico: str = Field(description="Párrafo de 2-3 oraciones describiendo el perfil caracterológico del estudiante de forma objetiva y profesional.")
    caracteristicas: str = Field(description="Párrafo de 3-4 oraciones describiendo conductas observables en el contexto académico universitario.")
    recomendaciones: str = Field(description="Párrafo de 3-4 oraciones con recomendaciones concretas para mejorar el rendimiento académico y bienestar emocional.")

# ---------------------------------------------------------------------------
# Prompt base — estructura fija; los valores se inyectan en tiempo de ejecución
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """
Eres un psicólogo clínico experto en el Cuestionario Caracterológico de Gastón Berger,
adaptación de Luis Vicuña Peri. Recibes los resultados de un estudiante universitario
de Ingeniería de Sistemas de la UNMSM y debes generar un informe psicológico profesional.

DATOS DEL EVALUADO:
- Perfil caracterológico: {nombre_perfil} ({codigo_tecnico})
- Puntaje Emotividad (E): {puntaje_e} / 90 (umbral E: 54)
- Puntaje Actividad (A): {puntaje_a} / 90 (umbral A: 52)
- Puntaje Resonancia (R): {puntaje_r} / 90 (umbral R: 52)
- Alerta por Emotividad alta (E > 75): {alerta_e}

IMPORTANTE:
- Usa lenguaje profesional pero comprensible para el estudiante.
- No uses listas ni viñetas; solo párrafos continuos.
- No inventes datos que no estén en los puntajes proporcionados.
"""


class CalculadorViaIA(ICalculadorPerfil):
    """
    Implementación que delega la interpretación cualitativa a Gemini.
    Usa CalculadorBergerInterno para los puntajes numéricos y la
    clasificación de perfil, luego llama a la API para la narrativa.
    """

    def __init__(self):
        self._berger = CalculadorBergerInterno()

    def calcular(self, sesion: SesionRespuesta, db: Session) -> dict:
        # Paso 1 — Calcular puntajes y perfil con el algoritmo interno
        resultado = self._berger.calcular(sesion, db)

        # Paso 2 — Obtener datos del perfil para el prompt
        perfil = None
        if resultado["id_perfil"]:
            perfil = db.query(PerfilPsicologico).filter_by(
                id_perfil=resultado["id_perfil"]
            ).first()

        # Paso 3 — Generar interpretación IA
        if perfil:
            interpretacion = self._generar_interpretacion(resultado, perfil)
            resultado["ia_diagnostico"]     = interpretacion.get("diagnostico")
            resultado["ia_caracteristicas"] = interpretacion.get("caracteristicas")
            resultado["ia_recomendaciones"] = interpretacion.get("recomendaciones")

        return resultado

    def _generar_interpretacion(
        self,
        resultado: dict,
        perfil: PerfilPsicologico,
    ) -> dict:
        """
        Llama a Gemini con el prompt estructurado.
        Si la API falla, retorna un dict vacío para no bloquear el flujo.
        """
        prompt = PROMPT_TEMPLATE.format(
            nombre_perfil=perfil.nombre_perfil,
            codigo_tecnico=perfil.descripcion_base[:10] if perfil.descripcion_base else "",
            puntaje_e=resultado["puntaje_emotividad"],
            puntaje_a=resultado["puntaje_actividad"],
            puntaje_r=resultado["puntaje_resonancia"],
            alerta_e="Sí" if resultado["alerta_emotividad_alta"] == "true" else "No",
        )

        try:
            # Forzamos a Gemini a responder en formato JSON puro mediante su API nativa
            configuracion_json = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InformePsicologico,
                temperature=0.2  # Consistencia y formalidad clínica
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                prompt=prompt,
                config=configuracion_json,
            )

            return json.loads(response.text)

        except Exception as e:
            # El fallo de IA no debe bloquear el resultado numérico
            print(f"[WARN] Gemini no disponible: {e}")
            return {}