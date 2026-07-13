from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.tamizaje import Tamizaje
from app.models.alumno import Alumno
from app.models.token_acceso import TokenAcceso
from app.schemas.tamizaje import TamizajeCreate, TamizajeUpdate, TamizajeConEstadistica
from app.services.token_service import generar_y_enviar_token


def crear_tamizaje(
    data: TamizajeCreate,
    id_personal: int,
    db: Session,
) -> Tamizaje:
    tamizaje = Tamizaje(
        id_personal_creador=id_personal,
        id_instrumento=data.id_instrumento,
        nombre=data.nombre,
        descripcion=data.descripcion,
        fecha_limite_respuesta=data.fecha_limite_respuesta,
        estado="borrador",
    )
    db.add(tamizaje)
    db.flush()
    return tamizaje


def listar_tamizajes(db: Session, estado: str | None = None) -> list[Tamizaje]:
    query = db.query(Tamizaje)
    if estado:
        query = query.filter_by(estado=estado)
    return query.order_by(Tamizaje.fecha_creacion.desc()).all()


def activar_tamizaje(id_tamizaje: int, db: Session) -> Tamizaje:
    tamizaje = _get_or_404(id_tamizaje, db)
    if tamizaje.estado != "borrador":
        raise HTTPException(
            status_code=400,
            detail=f"Solo los tamizajes en estado 'borrador' pueden activarse "
                   f"(estado actual: {tamizaje.estado}).",
        )
    tamizaje.estado = "activo"
    return tamizaje


def actualizar_tamizaje(
    id_tamizaje: int,
    data: TamizajeUpdate,
    db: Session,
) -> Tamizaje:
    tamizaje = _get_or_404(id_tamizaje, db)

    if tamizaje.estado not in ("borrador",):
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden editar tamizajes en estado 'borrador'.",
        )

    for campo, valor in data.model_dump(exclude_none=True).items():
        setattr(tamizaje, campo, valor)

    return tamizaje


def invitar_alumnos(
    id_tamizaje: int,
    ids_alumno: list[int],
    db: Session,
) -> dict:
    """
    Genera y envía tokens para una lista de alumnos en un tamizaje activo.
    Retorna un resumen de éxitos y fallos sin interrumpir el batch completo.
    """
    resultados = {"enviados": [], "fallidos": []}

    for id_alumno in ids_alumno:
        try:
            generar_y_enviar_token(id_tamizaje, id_alumno, db)
            resultados["enviados"].append(id_alumno)
        except HTTPException as e:
            resultados["fallidos"].append({
                "id_alumno": id_alumno,
                "motivo": e.detail,
            })

    return resultados


def listar_tokens_de_tamizaje(id_tamizaje: int, db: Session) -> list[TokenAcceso]:
    _get_or_404(id_tamizaje, db)
    return (
        db.query(TokenAcceso)
        .filter_by(id_tamizaje=id_tamizaje)
        .join(Alumno, TokenAcceso.id_alumno == Alumno.id_alumno)
        .order_by(Alumno.nombre_completo)
        .all()
    )


def obtener_estadisticas(
    id_tamizaje: int,
    db: Session,
) -> TamizajeConEstadistica:
    tamizaje = _get_or_404(id_tamizaje, db)

    total_invitados = db.query(TokenAcceso).filter_by(
        id_tamizaje=id_tamizaje
    ).count()

    total_respondidos = db.query(TokenAcceso).filter_by(
        id_tamizaje=id_tamizaje,
        estado="usado",
    ).count()

    return TamizajeConEstadistica(
        **tamizaje.__dict__,
        total_invitados=total_invitados,
        total_respondidos=total_respondidos,
        total_pendientes=total_invitados - total_respondidos,
    )


def _get_or_404(id_tamizaje: int, db: Session) -> Tamizaje:
    tamizaje = db.query(Tamizaje).filter_by(id_tamizaje=id_tamizaje).first()
    if not tamizaje:
        raise HTTPException(status_code=404, detail="Tamizaje no encontrado.")
    return tamizaje