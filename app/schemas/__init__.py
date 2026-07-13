from app.schemas.auth import TokenResponse, LoginRequest
from app.schemas.alumno import AlumnoCreate, AlumnoRead, AlumnoUpdate
from app.schemas.tamizaje import TamizajeCreate, TamizajeRead, TamizajeUpdate
from app.schemas.token_acceso import TokenAccesoRead, TokenRegenerateRequest
from app.schemas.sesion_respuesta import SesionInicioRead, RespuestaEnvioRequest
from app.schemas.resultado import ResultadoRead, ResultadoResumen
from app.schemas.disponibilidad import DisponibilidadCreate, DisponibilidadRead
from app.schemas.cita import CitaCreate, CitaRead, CitaUpdate
from app.schemas.instrumento import InstrumentoRead