from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.token_acceso import TokenAcceso
from app.models.alumno import Alumno
from app.models.tamizaje import Tamizaje
from app.utils.security import generate_raw_token, hash_token
from app.utils.email import enviar_token_cuestionario
from app.config import get_settings

settings = get_settings()

def _get_tamizaje_activo(id_tamizaje: int, db: Session) -> Tamizaje:
    tamizaje = db.query(Tamizaje).filter_by(id_tamizaje=id_tamizaje).first()
    if not tamizaje:
        raise HTTPException(status_code=404, detail="Tamizaje no encontrado.")
    if tamizaje.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El tamizaje no está activo (estado actual: {tamizaje.estado}).",
        )
    return tamizaje


def generar_y_enviar_token(
    id_tamizaje: int,
    id_alumno: int,
    db: Session,
) -> TokenAcceso:
    """
    Genera un token de acceso para un alumno en un tamizaje y lo envía por email.
    Si ya existe un token pendiente para el mismo par, lanza error.
    """
    tamizaje = _get_tamizaje_activo(id_tamizaje, db)

    alumno = db.query(Alumno).filter_by(id_alumno=id_alumno).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado.")

    # Verificar que no exista ya un token pendiente para este par
    existente = db.query(TokenAcceso).filter_by(
        id_tamizaje=id_tamizaje,
        id_alumno=id_alumno,
        estado="pendiente",
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un token pendiente para este alumno en este tamizaje.",
        )

    raw_token = generate_raw_token()
    token = TokenAcceso(
        id_tamizaje=id_tamizaje,
        id_alumno=id_alumno,
        token_hash=hash_token(raw_token),
        fecha_expiracion=tamizaje.fecha_limite_respuesta,
        estado="pendiente",
    )
    db.add(token)
    db.flush()

    # Envío de email con el token en texto plano
    enviar_token_cuestionario(
        to_email=alumno.email_institucional,
        nombre_alumno=alumno.nombre_completo,
        nombre_tamizaje=tamizaje.nombre,
        raw_token=raw_token,
        fecha_limite=tamizaje.fecha_limite_respuesta.strftime("%d/%m/%Y %H:%M"),
        base_url=settings.frontend_url,
    )

    return token


def regenerar_token(
    id_tamizaje: int,
    id_alumno: int,
    db: Session,
) -> TokenAcceso:
    """
    Invalida el token actual del alumno en el tamizaje (si existe)
    y genera uno nuevo. Cubre la RN-05 actualizada.
    Ejecutado en una sola transacción por el caller (service o router).
    """
    _get_tamizaje_activo(id_tamizaje, db)

    # Invalidar token anterior si existe
    token_anterior = db.query(TokenAcceso).filter_by(
        id_tamizaje=id_tamizaje,
        id_alumno=id_alumno,
    ).filter(TokenAcceso.estado.in_(["pendiente", "expirado"])).first()

    if token_anterior:
        token_anterior.estado = "anulado"
        db.flush()

    return generar_y_enviar_token(id_tamizaje, id_alumno, db)


def validar_token(raw_token: str, db: Session) -> TokenAcceso:
    """
    Valida el token recibido del alumno.
    Retorna el TokenAcceso si es válido.
    Lanza HTTPException en cualquier caso de rechazo.
    """
    token_hash = hash_token(raw_token)
    token = db.query(TokenAcceso).filter_by(token_hash=token_hash).first()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El enlace de acceso no es válido.",
        )

    if token.estado == "usado":
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este enlace ya fue utilizado. El cuestionario fue completado.",
        )

    if token.estado == "anulado":
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este enlace fue anulado. Contacte a UNAYOE para obtener uno nuevo.",
        )

    if token.fecha_expiracion < datetime.now(timezone.utc):
        token.estado = "expirado"
        db.flush()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="El enlace ha expirado. Contacte a UNAYOE para solicitar uno nuevo.",
        )

    return token