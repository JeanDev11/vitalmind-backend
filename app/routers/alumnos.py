from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.personal import Personal
from app.models.alumno import Alumno
from app.schemas.alumno import AlumnoCreate, AlumnoUpdate, AlumnoRead

router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnos"],
    dependencies=[Depends(get_current_user)],   # Todos los endpoints requieren JWT
)


@router.post("/", response_model=AlumnoRead, status_code=status.HTTP_201_CREATED)
def crear_alumno(
    data: AlumnoCreate,
    db: Session = Depends(get_db),
):
    """Registra un nuevo alumno. Valida unicidad de DNI, código y email."""
    alumno = Alumno(**data.model_dump())
    db.add(alumno)
    db.commit()
    db.refresh(alumno)
    return alumno


@router.get("/", response_model=list[AlumnoRead])
def listar_alumnos(
    estado: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Lista todos los alumnos.
    Filtra opcionalmente por estado: activo | inactivo | desertor | egresado.
    """
    query = db.query(Alumno)
    if estado:
        query = query.filter_by(estado=estado)
    return query.order_by(Alumno.nombre_completo).all()


@router.get("/{id_alumno}", response_model=AlumnoRead)
def obtener_alumno(id_alumno: int, db: Session = Depends(get_db)):
    """Devuelve el detalle de un alumno por ID."""
    alumno = db.query(Alumno).filter_by(id_alumno=id_alumno).first()
    if not alumno:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alumno no encontrado.")
    return alumno


@router.put("/{id_alumno}", response_model=AlumnoRead)
def actualizar_alumno(
    id_alumno: int,
    data: AlumnoUpdate,
    db: Session = Depends(get_db),
):
    """Actualiza campos editables del alumno (nombre, email, ciclo, estado)."""
    from fastapi import HTTPException
    alumno = db.query(Alumno).filter_by(id_alumno=id_alumno).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado.")

    for campo, valor in data.model_dump(exclude_none=True).items():
        setattr(alumno, campo, valor)

    db.commit()
    db.refresh(alumno)
    return alumno