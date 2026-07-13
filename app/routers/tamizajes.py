from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.personal import Personal
from app.schemas.tamizaje import TamizajeCreate, TamizajeRead, TamizajeUpdate, TamizajeConEstadistica
from app.schemas.token_acceso import TokenRegenerateRequest, TokenAccesoConAlumnoRead
from app.services import tamizaje_service, token_service
from app.utils.security import get_current_personal

router = APIRouter()


@router.post("/", response_model=TamizajeRead, status_code=201)
def crear_tamizaje(
    data: TamizajeCreate,
    db: Session = Depends(get_db),
    personal: Personal = Depends(get_current_personal),
):
    """Crea un nuevo tamizaje en estado 'borrador'."""
    tamizaje = tamizaje_service.crear_tamizaje(data, personal.id_personal, db)
    db.commit()
    db.refresh(tamizaje)
    return tamizaje


@router.get("/", response_model=List[TamizajeRead])
def listar_tamizajes(
    estado: str | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """Lista todos los tamizajes, opcionalmente filtrados por estado."""
    return tamizaje_service.listar_tamizajes(db, estado)


@router.patch("/{id_tamizaje}", response_model=TamizajeRead)
def actualizar_tamizaje(
    id_tamizaje: int,
    data: TamizajeUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """Edita un tamizaje en estado 'borrador'."""
    tamizaje = tamizaje_service.actualizar_tamizaje(id_tamizaje, data, db)
    db.commit()
    db.refresh(tamizaje)
    return tamizaje


@router.post("/{id_tamizaje}/activar", response_model=TamizajeRead)
def activar_tamizaje(
    id_tamizaje: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """Cambia el estado del tamizaje de 'borrador' a 'activo'."""
    tamizaje = tamizaje_service.activar_tamizaje(id_tamizaje, db)
    db.commit()
    db.refresh(tamizaje)
    return tamizaje


@router.post("/{id_tamizaje}/invitar")
def invitar_alumnos(
    id_tamizaje: int,
    ids_alumno: List[int],
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """
    Genera y envía tokens a una lista de alumnos para un tamizaje activo.
    Retorna resumen de enviados y fallidos.
    """
    resultado = tamizaje_service.invitar_alumnos(id_tamizaje, ids_alumno, db)
    db.commit()
    return resultado


@router.post("/tokens/regenerar")
def regenerar_token(
    data: TokenRegenerateRequest,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """
    Invalida el token actual de un alumno en un tamizaje
    y genera uno nuevo. Cubre RN-05.
    """
    token_service.regenerar_token(data.id_tamizaje, data.id_alumno, db)
    db.commit()
    return {"detail": "Token regenerado y enviado al alumno exitosamente."}


@router.get("/{id_tamizaje}/tokens", response_model=List[TokenAccesoConAlumnoRead])
def listar_tokens(
    id_tamizaje: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """Lista los alumnos invitados a un tamizaje con el estado de su token de acceso."""
    tokens = tamizaje_service.listar_tokens_de_tamizaje(id_tamizaje, db)
    return [
        TokenAccesoConAlumnoRead(
            id_token=t.id_token,
            id_alumno=t.id_alumno,
            nombre_alumno=t.alumno.nombre_completo,
            codigo_matricula=t.alumno.codigo_matricula,
            estado=t.estado,
            fecha_expiracion=t.fecha_expiracion,
            fecha_uso=t.fecha_uso,
        )
        for t in tokens
    ]


@router.get("/{id_tamizaje}/estadisticas", response_model=TamizajeConEstadistica)
def estadisticas_tamizaje(
    id_tamizaje: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """Panel de estado del tamizaje: invitados, respondidos y pendientes."""
    return tamizaje_service.obtener_estadisticas(id_tamizaje, db)