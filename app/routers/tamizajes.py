from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.personal import Personal
from app.schemas.tamizaje import (
    TamizajeCreate, TamizajeUpdate, TamizajeRead, TamizajeConEstadistica,
)
from app.schemas.token_acceso import TokenRegenerateRequest, TokenAccesoRead
from app.services import tamizaje_service
from app.services import token_service

router = APIRouter(
    prefix="/tamizajes",
    tags=["Tamizajes"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=TamizajeRead, status_code=status.HTTP_201_CREATED)
def crear_tamizaje(
    data: TamizajeCreate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user),
):
    """Crea un tamizaje en estado 'borrador'. Solo el personal autenticado puede crearlo."""
    tamizaje = tamizaje_service.crear_tamizaje(data, current_user.id_personal, db)
    db.commit()
    db.refresh(tamizaje)
    return tamizaje


@router.get("/", response_model=list[TamizajeRead])
def listar_tamizajes(
    estado: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Lista todos los tamizajes.
    Filtra opcionalmente por estado: borrador | activo | cerrado | anulado.
    """
    from app.models.tamizaje import Tamizaje
    query = db.query(Tamizaje)
    if estado:
        query = query.filter_by(estado=estado)
    return query.order_by(Tamizaje.fecha_creacion.desc()).all()


@router.get("/{id_tamizaje}", response_model=TamizajeConEstadistica)
def obtener_tamizaje(id_tamizaje: int, db: Session = Depends(get_db)):
    """Devuelve el tamizaje con estadísticas de invitados y respondidos."""
    return tamizaje_service.obtener_estadisticas(id_tamizaje, db)


@router.put("/{id_tamizaje}", response_model=TamizajeRead)
def actualizar_tamizaje(
    id_tamizaje: int,
    data: TamizajeUpdate,
    db: Session = Depends(get_db),
):
    """Edita campos del tamizaje. Solo permitido en estado 'borrador'."""
    tamizaje = tamizaje_service.actualizar_tamizaje(id_tamizaje, data, db)
    db.commit()
    db.refresh(tamizaje)
    return tamizaje


@router.patch("/{id_tamizaje}/activar", response_model=TamizajeRead)
def activar_tamizaje(id_tamizaje: int, db: Session = Depends(get_db)):
    """
    Cambia el estado del tamizaje de 'borrador' a 'activo'.
    A partir de este momento se pueden enviar tokens a los alumnos.
    """
    tamizaje = tamizaje_service.activar_tamizaje(id_tamizaje, db)
    db.commit()
    db.refresh(tamizaje)
    return tamizaje


@router.post("/{id_tamizaje}/invitar")
def invitar_alumnos(
    id_tamizaje: int,
    ids_alumno: list[int],
    db: Session = Depends(get_db),
):
    """
    Genera y envía tokens de acceso por email a una lista de alumnos.
    Retorna un resumen con los enviados y los fallidos (p.ej. token duplicado).
    El tamizaje debe estar en estado 'activo'.
    """
    resultado = tamizaje_service.invitar_alumnos(id_tamizaje, ids_alumno, db)
    db.commit()
    return resultado


@router.post("/{id_tamizaje}/regenerar-token", response_model=TokenAccesoRead)
def regenerar_token(
    id_tamizaje: int,
    body: TokenRegenerateRequest,
    db: Session = Depends(get_db),
):
    """
    Invalida el token anterior del alumno (pendiente o expirado)
    y genera uno nuevo enviándolo por email. Cubre RN-05.
    """
    token = token_service.regenerar_token(id_tamizaje, body.id_alumno, db)
    db.commit()
    db.refresh(token)
    return token