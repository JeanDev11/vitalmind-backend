from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.sesion_respuesta import SesionRespuesta
from app.schemas.sesion_respuesta import (
    SesionInicioRead,
    PreguntaResumenRead,
    OpcionResumenRead,
    RespuestaEnvioRequest,
    SesionEstadoRead,
)
from app.services.token_service import validar_token
from app.services.resultado_service import persistir_respuestas_y_calcular

router = APIRouter()


@router.get("/iniciar", response_model=SesionInicioRead)
def iniciar_cuestionario(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Endpoint público — acceso exclusivo por token de negocio.
    Valida el token, crea la SesionRespuesta y retorna las preguntas.
    El alumno no requiere JWT.
    """
    token_obj = validar_token(token, db)

    # Verificar si ya existe una sesión para este token
    sesion_existente = db.query(SesionRespuesta).filter_by(
        id_token=token_obj.id_token
    ).first()

    if sesion_existente and sesion_existente.estado == "enviada":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=410,
            detail="El cuestionario ya fue completado.",
        )

    # Crear sesión si no existe aún
    if not sesion_existente:
        sesion = SesionRespuesta(
            id_token=token_obj.id_token,
            id_tamizaje=token_obj.id_tamizaje,
            id_alumno=token_obj.id_alumno,
            fecha_inicio=datetime.now(timezone.utc),
            estado="en_progreso",
        )
        db.add(sesion)
        db.commit()
        db.refresh(sesion)
    else:
        sesion = sesion_existente

    # Construir respuesta con las preguntas del instrumento
    instrumento = token_obj.tamizaje.instrumento
    preguntas = sorted(instrumento.preguntas, key=lambda p: p.orden)

    preguntas_schema = [
        PreguntaResumenRead(
            id_pregunta=p.id_pregunta,
            orden=p.orden,
            enunciado=p.enunciado,
            dimension=p.dimension,
            tipo_respuesta=p.tipo_respuesta,
            opciones=[
                OpcionResumenRead(
                    id_opcion=o.id_opcion,
                    texto_opcion=o.texto_opcion,
                    orden=o.orden,
                )
                for o in sorted(p.opciones, key=lambda o: o.orden)
            ],
        )
        for p in preguntas
        if p.activo
    ]

    return SesionInicioRead(
        id_sesion=sesion.id_sesion,
        nombre_instrumento=instrumento.nombre,
        preguntas=preguntas_schema,
    )


@router.post("/enviar", response_model=SesionEstadoRead)
def enviar_cuestionario(
    payload: RespuestaEnvioRequest,
    db: Session = Depends(get_db),
):
    """
    Endpoint público — recibe las respuestas del alumno y ejecuta
    el flujo atómico de envío: persiste respuestas, marca token como usado,
    calcula el perfil y persiste el resultado.
    """
    sesion = db.query(SesionRespuesta).filter_by(
        id_sesion=payload.id_sesion
    ).first()

    if not sesion:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    persistir_respuestas_y_calcular(sesion, payload, db)
    db.commit()
    db.refresh(sesion)

    return SesionEstadoRead(
        id_sesion=sesion.id_sesion,
        estado=sesion.estado,
        fecha_inicio=sesion.fecha_inicio,
        fecha_envio=sesion.fecha_envio,
    )