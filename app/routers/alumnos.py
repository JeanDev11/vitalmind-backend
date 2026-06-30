from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.alumno import Alumno
from app.models.personal import Personal
from app.schemas.alumno import AlumnoCreate, AlumnoRead, AlumnoUpdate
from app.utils.security import get_current_personal

router = APIRouter()


@router.post("/", response_model=AlumnoRead, status_code=201)
def crear_alumno(
    data: AlumnoCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """Registra un alumno nuevo en el padrón."""
    if db.query(Alumno).filter_by(codigo_matricula=data.codigo_matricula).first():
        raise HTTPException(status_code=409, detail="El código de matrícula ya existe.")
    if db.query(Alumno).filter_by(dni=data.dni).first():
        raise HTTPException(status_code=409, detail="El DNI ya está registrado.")

    alumno = Alumno(**data.model_dump())
    db.add(alumno)
    db.commit()
    db.refresh(alumno)
    return alumno


@router.post("/bulk", status_code=201)
def crear_alumnos_bulk(
    alumnos: List[AlumnoCreate],
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """
    Carga masiva del padrón (cohorte de ingresantes).
    Retorna resumen de insertados y duplicados sin interrumpir el batch.
    """
    insertados = []
    duplicados = []

    for data in alumnos:
        existe = (
            db.query(Alumno)
            .filter(
                (Alumno.codigo_matricula == data.codigo_matricula)
                | (Alumno.dni == data.dni)
            )
            .first()
        )
        if existe:
            duplicados.append(data.codigo_matricula)
            continue

        alumno = Alumno(**data.model_dump())
        db.add(alumno)
        insertados.append(data.codigo_matricula)

    db.commit()
    return {
        "insertados": len(insertados),
        "duplicados": len(duplicados),
        "detalle_duplicados": duplicados,
    }


@router.get("/", response_model=List[AlumnoRead])
def listar_alumnos(
    codigo: str | None = None,
    nombre: str | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """
    Lista alumnos con filtros opcionales.
    Permite buscar por código de matrícula, nombre parcial o estado.
    """
    query = db.query(Alumno)
    if codigo:
        query = query.filter(Alumno.codigo_matricula.ilike(f"%{codigo}%"))
    if nombre:
        query = query.filter(Alumno.nombre_completo.ilike(f"%{nombre}%"))
    if estado:
        query = query.filter_by(estado=estado)
    return query.order_by(Alumno.nombre_completo).all()


@router.get("/{id_alumno}", response_model=AlumnoRead)
def obtener_alumno(
    id_alumno: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    alumno = db.query(Alumno).filter_by(id_alumno=id_alumno).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado.")
    return alumno


@router.patch("/{id_alumno}", response_model=AlumnoRead)
def actualizar_alumno(
    id_alumno: int,
    data: AlumnoUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    alumno = db.query(Alumno).filter_by(id_alumno=id_alumno).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado.")

    for campo, valor in data.model_dump(exclude_none=True).items():
        setattr(alumno, campo, valor)

    db.commit()
    db.refresh(alumno)
    return alumno