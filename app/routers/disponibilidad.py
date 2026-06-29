from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.personal import Personal
from app.models.disponibilidad import Disponibilidad
from app.schemas.disponibilidad import DisponibilidadCreate, DisponibilidadRead

router = APIRouter(
    prefix="/disponibilidad",
    tags=["Disponibilidad"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=DisponibilidadRead, status_code=status.HTTP_201_CREATED)
def crear_slot(
    data: DisponibilidadCreate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user),
):
    """
    Registra un slot de disponibilidad para el personal autenticado.
    La restricción uq_slot_personal evita duplicados en BD.
    """
    slot = Disponibilidad(
        id_personal=current_user.id_personal,
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        disponible=True,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.get("/", response_model=list[DisponibilidadRead])
def listar_slots(
    solo_disponibles: bool = False,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user),
):
    """
    Lista los slots del personal autenticado.
    Con solo_disponibles=true filtra los que aún no tienen cita asignada.
    """
    query = db.query(Disponibilidad).filter_by(id_personal=current_user.id_personal)
    if solo_disponibles:
        query = query.filter_by(disponible=True)
    return query.order_by(Disponibilidad.fecha, Disponibilidad.hora_inicio).all()


@router.delete("/{id_slot}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_slot(
    id_slot: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user),
):
    """
    Elimina un slot propio que aún esté disponible.
    No se puede eliminar un slot con cita activa asignada.
    """
    slot = db.query(Disponibilidad).filter_by(
        id_slot=id_slot,
        id_personal=current_user.id_personal,
    ).first()

    if not slot:
        raise HTTPException(
            status_code=404,
            detail="Slot no encontrado o no pertenece al usuario autenticado.",
        )

    if not slot.disponible:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un slot con una cita activa asignada.",
        )

    db.delete(slot)
    db.commit()