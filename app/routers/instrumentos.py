from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.personal import Personal
from app.models.instrumento import Instrumento
from app.schemas.instrumento import InstrumentoRead
from app.utils.security import get_current_personal

router = APIRouter()


@router.get("/", response_model=List[InstrumentoRead])
def listar_instrumentos(
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """Lista los instrumentos de evaluación disponibles para crear tamizajes."""
    query = db.query(Instrumento)
    if solo_activos:
        query = query.filter_by(activo=True)
    return query.order_by(Instrumento.nombre).all()
