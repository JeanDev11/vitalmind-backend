"""
Portal del alumno — acceso exclusivo mediante token de negocio (NO JWT).
Los alumnos nunca reciben un JWT; su credencial es el enlace de un solo uso.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sesion_respuesta import SesionRespuesta
from app.models.instrumento import Instrumento
from app.models.pregunta import Pregunta
from app.models.opcion_respuesta import OpcionRespuesta
from app.schemas.sesion_respuesta import (
    SesionInicioRead,
    PreguntaResumenRead,
    OpcionResumenRead,
    RespuestaEnvioRequest,
    SesionEstadoRead,
)
from app.services.token_service import validar_token
from app.services.resultado_service import persistir_respuestas_y_calcular

router = APIRouter(prefix="/cuestionario", tags=["Cuestionario (Alumno)"])


class TokenInicioRequest:
    """Body para iniciar sesión con token en texto plano."""
    def __init__(self, token: str):
        self.token = token


from pydantic import BaseModel

class IniciarRequest(BaseModel):
    token: str

class EnviarRequest(RespuestaEnvioRequest):
    """Extiende RespuestaEnvioRequest — no agrega campos, solo documenta el contexto."""
    pass


@router.post("/iniciar", response_model=SesionInicioRead)
def iniciar_cuestionario(body: IniciarRequest, db: Session = Depends(get_db)):
    """
    El alumno accede con su token de un solo uso.
    1. Valida el token (estado, expiración).
    2. Crea la SesionRespuesta si no existe (idempotente en 'iniciada').
    3. Devuelve el instrumento con todas las preguntas y opciones.
    """
    token_obj = validar_token(body.token, db)

    # Buscar sesión existente para este token (idempotencia)
    sesion = db.query(SesionRespuesta).filter_by(
        id_token=token_obj.id_token
    ).first()

    if sesion and sesion.estado == "enviada":
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este cuestionario ya fue completado y enviado.",
        )

    if not sesion:
        sesion = SesionRespuesta(
            id_token=token_obj.id_token,
            id_tamizaje=token_obj.id_tamizaje,
            id_alumno=token_obj.id_alumno,
            fecha_inicio=datetime.now(timezone.utc),
            estado="iniciada",
        )
        db.add(sesion)
        db.flush()

    # Cargar instrumento y preguntas ordenadas
    instrumento = db.query(Instrumento).filter_by(
        id_instrumento=token_obj.tamizaje.id_instrumento
    ).first()

    if not instrumento:
        raise HTTPException(status_code=500, detail="Instrumento no configurado.")

    preguntas_db = (
        db.query(Pregunta)
        .filter_by(id_instrumento=instrumento.id_instrumento)
        .order_by(Pregunta.orden)
        .all()
    )

    preguntas_out = []
    for p in preguntas_db:
        opciones_db = (
            db.query(OpcionRespuesta)
            .filter_by(id_pregunta=p.id_pregunta)
            .order_by(OpcionRespuesta.orden)
            .all()
        )
        opciones_out = [
            OpcionResumenRead.model_validate(o) for o in opciones_db
        ]
        preguntas_out.append(
            PreguntaResumenRead(
                id_pregunta=p.id_pregunta,
                orden=p.orden,
                enunciado=p.enunciado,
                dimension=p.dimension,
                tipo_respuesta=p.tipo_respuesta,
                opciones=opciones_out,
            )
        )

    db.commit()

    return SesionInicioRead(
        id_sesion=sesion.id_sesion,
        nombre_instrumento=instrumento.nombre,
        preguntas=preguntas_out,
    )


@router.post("/enviar", response_model=SesionEstadoRead)
def enviar_cuestionario(
    body: RespuestaEnvioRequest,
    db: Session = Depends(get_db),
):
    """
    El alumno envía todas sus respuestas en un único request (RN-03).
    Persiste ítems, cierra la sesión, marca el token como usado y calcula el perfil.
    Todo en una sola transacción.
    """
    sesion = db.query(SesionRespuesta).filter_by(
        id_sesion=body.id_sesion
    ).first()

    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    persistir_respuestas_y_calcular(sesion, body, db)
    db.commit()
    db.refresh(sesion)
    return sesion