# Importar todos los modelos para que Alembic los detecte automáticamente
from app.models.personal import Personal
from app.models.alumno import Alumno
from app.models.instrumento import Instrumento
from app.models.pregunta import Pregunta
from app.models.opcion_respuesta import OpcionRespuesta
from app.models.perfil_psicologico import PerfilPsicologico
from app.models.tamizaje import Tamizaje
from app.models.token_acceso import TokenAcceso
from app.models.sesion_respuesta import SesionRespuesta
from app.models.respuesta_item import RespuestaItem
from app.models.resultado_tamizaje import ResultadoTamizaje
from app.models.disponibilidad import Disponibilidad
from app.models.cita import Cita
from app.models.historia_clinica import HistoriaClinica