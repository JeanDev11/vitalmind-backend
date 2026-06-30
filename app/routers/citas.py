from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.personal import Personal
from app.schemas.cita import CitaCreate, CitaRead, CitaUpdate
from app.services.cita_service import crear_cita, actualizar_cita, listar_citas_personal
from app.utils.security import get_current_personal

router = APIRouter()


@router.post("/", response_model=CitaRead, status_code=201)
def agendar_cita(
    data: CitaCreate,
    db: Session = Depends(get_db),
    personal: Personal = Depends(get_current_personal),
):
    """
    Agenda una cita para un alumno en un slot disponible.
    Puede originarse desde un resultado de tamizaje (proactiva)
    o sin resultado asociado (demanda espontánea).
    """
    cita = crear_cita(data, personal.id_personal, db)
    db.commit()
    db.refresh(cita)

    return CitaRead(
        id_cita=cita.id_cita,
        id_slot=cita.id_slot,
        id_alumno=cita.id_alumno,
        nombre_alumno=cita.alumno.nombre_completo,
        id_personal=cita.id_personal,
        id_resultado_origen=cita.id_resultado_origen,
        motivo=cita.motivo,
        estado=cita.estado,
        notas_sesion=cita.notas_sesion,
        fecha_creacion=cita.fecha_creacion,
    )


@router.patch("/{id_cita}", response_model=CitaRead)
def actualizar_estado_cita(
    id_cita: int,
    data: CitaUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """
    Actualiza el estado de una cita o agrega notas de sesión.
    La cancelación libera el slot automáticamente (RN-07).
    """
    cita = actualizar_cita(id_cita, data, db)
    db.commit()
    db.refresh(cita)

    return CitaRead(
        id_cita=cita.id_cita,
        id_slot=cita.id_slot,
        id_alumno=cita.id_alumno,
        nombre_alumno=cita.alumno.nombre_completo,
        id_personal=cita.id_personal,
        id_resultado_origen=cita.id_resultado_origen,
        motivo=cita.motivo,
        estado=cita.estado,
        notas_sesion=cita.notas_sesion,
        fecha_creacion=cita.fecha_creacion,
    )


@router.get("/", response_model=List[CitaRead])
def listar_citas(
    db: Session = Depends(get_db),
    personal: Personal = Depends(get_current_personal),
):
    """Lista todas las citas de la psicóloga autenticada."""
    citas = listar_citas_personal(personal.id_personal, db)

    return [
        CitaRead(
            id_cita=c.id_cita,
            id_slot=c.id_slot,
            id_alumno=c.id_alumno,
            nombre_alumno=c.alumno.nombre_completo,
            id_personal=c.id_personal,
            id_resultado_origen=c.id_resultado_origen,
            motivo=c.motivo,
            estado=c.estado,
            notas_sesion=c.notas_sesion,
            fecha_creacion=c.fecha_creacion,
        )
        for c in citas
    ]