from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.personal import Personal
from app.schemas.cita import CitaCreate, CitaUpdate, CitaRead
from app.services import cita_service

router = APIRouter(
    prefix="/citas",
    tags=["Citas"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=CitaRead, status_code=status.HTTP_201_CREATED)
def crear_cita(
    data: CitaCreate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user),
):
    """
    Agenda una cita en un slot disponible para un alumno.
    Envía confirmación por email al alumno (RN-06).
    """
    cita = cita_service.crear_cita(data, current_user.id_personal, db)
    db.commit()
    db.refresh(cita)
    return cita


@router.get("/", response_model=list[CitaRead])
def listar_citas(
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user),
):
    """Lista todas las citas agendadas por el personal autenticado."""
    return cita_service.listar_citas_personal(current_user.id_personal, db)


@router.patch("/{id_cita}", response_model=CitaRead)
def actualizar_cita(
    id_cita: int,
    data: CitaUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza el estado y/o las notas de sesión de una cita.
    Cancelar o marcar como no_asistio libera el slot automáticamente (RN-07).
    """
    cita = cita_service.actualizar_cita(id_cita, data, db)
    db.commit()
    db.refresh(cita)
    return cita