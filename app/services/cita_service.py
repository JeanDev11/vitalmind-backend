from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.cita import Cita
from app.models.disponibilidad import Disponibilidad
from app.models.alumno import Alumno
from app.schemas.cita import CitaCreate, CitaUpdate
from app.utils.email import enviar_confirmacion_cita


def crear_cita(data: CitaCreate, id_personal: int, db: Session) -> Cita:
    # Verificar que el slot existe y está disponible
    slot = db.query(Disponibilidad).filter_by(
        id_slot=data.id_slot,
        disponible=True,
    ).first()

    if not slot:
        raise HTTPException(
            status_code=404,
            detail="El slot no existe o ya no está disponible.",
        )

    # Verificar que no exista una cita activa en ese slot (RN-06)
    cita_existente = db.query(Cita).filter(
        Cita.id_slot == data.id_slot,
        Cita.estado.in_(["programada", "completada"]),
    ).first()

    if cita_existente:
        raise HTTPException(
            status_code=409,
            detail="El slot ya tiene una cita activa asignada.",
        )

    alumno = db.query(Alumno).filter_by(id_alumno=data.id_alumno).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado.")

    cita = Cita(
        id_slot=data.id_slot,
        id_alumno=data.id_alumno,
        id_personal=id_personal,
        id_resultado_origen=data.id_resultado_origen,
        motivo=data.motivo,
        estado="programada",
    )
    db.add(cita)

    # Bloquear el slot
    slot.disponible = False
    db.flush()

    # Notificación al alumno
    enviar_confirmacion_cita(
        to_email=alumno.email_institucional,
        nombre_alumno=alumno.nombre_completo,
        fecha=slot.fecha.strftime("%d/%m/%Y"),
        hora=slot.hora_inicio.strftime("%H:%M"),
    )

    return cita


def actualizar_cita(
    id_cita: int,
    data: CitaUpdate,
    db: Session,
) -> Cita:
    cita = _get_or_404(id_cita, db)

    if data.estado:
        cita.estado = data.estado
        # RN-07 — Cancelación libera el slot
        if data.estado in ("cancelada", "no_asistio"):
            slot = db.query(Disponibilidad).filter_by(
                id_slot=cita.id_slot
            ).first()
            if slot:
                slot.disponible = True

    if data.notas_sesion is not None:
        cita.notas_sesion = data.notas_sesion

    db.flush()
    return cita


def listar_citas_personal(id_personal: int, db: Session) -> list[Cita]:
    return db.query(Cita).filter_by(id_personal=id_personal).all()


def _get_or_404(id_cita: int, db: Session) -> Cita:
    cita = db.query(Cita).filter_by(id_cita=id_cita).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada.")
    return cita