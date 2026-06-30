from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models.personal import Personal
from app.models.disponibilidad import Disponibilidad
from app.schemas.disponibilidad import DisponibilidadCreate, DisponibilidadRead
from app.utils.security import get_current_personal

router = APIRouter()


@router.post("/", response_model=DisponibilidadRead, status_code=201)
def crear_slot(
    data: DisponibilidadCreate,
    db: Session = Depends(get_db),
    personal: Personal = Depends(get_current_personal),
):
    """Registra un slot de disponibilidad para la psicóloga."""
    existente = db.query(Disponibilidad).filter_by(
        id_personal=personal.id_personal,
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
    ).first()

    if existente:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un slot en esa fecha y hora.",
        )

    slot = Disponibilidad(
        id_personal=personal.id_personal,
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        disponible=True,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.post("/bulk", status_code=201)
def crear_slots_bulk(
    slots: List[DisponibilidadCreate],
    db: Session = Depends(get_db),
    personal: Personal = Depends(get_current_personal),
):
    """
    Carga masiva de slots de disponibilidad.
    Útil para configurar la agenda semanal de una vez.
    """
    insertados = 0
    duplicados = 0

    for data in slots:
        existente = db.query(Disponibilidad).filter_by(
            id_personal=personal.id_personal,
            fecha=data.fecha,
            hora_inicio=data.hora_inicio,
        ).first()

        if existente:
            duplicados += 1
            continue

        slot = Disponibilidad(
            id_personal=personal.id_personal,
            fecha=data.fecha,
            hora_inicio=data.hora_inicio,
            hora_fin=data.hora_fin,
            disponible=True,
        )
        db.add(slot)
        insertados += 1

    db.commit()
    return {"insertados": insertados, "duplicados": duplicados}


@router.get("/", response_model=List[DisponibilidadRead])
def listar_slots(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    solo_disponibles: bool = True,
    db: Session = Depends(get_db),
    personal: Personal = Depends(get_current_personal),
):
    """Lista los slots de disponibilidad de la psicóloga autenticada."""
    query = db.query(Disponibilidad).filter_by(id_personal=personal.id_personal)

    if solo_disponibles:
        query = query.filter_by(disponible=True)
    if fecha_desde:
        query = query.filter(Disponibilidad.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Disponibilidad.fecha <= fecha_hasta)

    return query.order_by(Disponibilidad.fecha, Disponibilidad.hora_inicio).all()


@router.delete("/{id_slot}", status_code=204)
def eliminar_slot(
    id_slot: int,
    db: Session = Depends(get_db),
    personal: Personal = Depends(get_current_personal),
):
    """Elimina un slot disponible. No permite eliminar slots con cita asignada."""
    slot = db.query(Disponibilidad).filter_by(
        id_slot=id_slot,
        id_personal=personal.id_personal,
    ).first()

    if not slot:
        raise HTTPException(status_code=404, detail="Slot no encontrado.")
    if not slot.disponible:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar un slot con cita asignada.",
        )

    db.delete(slot)
    db.commit()