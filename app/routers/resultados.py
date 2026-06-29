from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.resultado_tamizaje import ResultadoTamizaje
from app.models.alumno import Alumno
from app.models.perfil_psicologico import PerfilPsicologico
from app.schemas.resultado import ResultadoRead, ResultadoResumen, SolicitudInterpretacionIA
from app.services.resultado_service import solicitar_interpretacion_ia

router = APIRouter(
    prefix="/resultados",
    tags=["Resultados"],
    dependencies=[Depends(get_current_user)],
)


def _enriquecer(resultado: ResultadoTamizaje, db: Session) -> dict:
    """
    Combina el ORM con datos de relaciones para cubrir los campos
    nombre_alumno, codigo_matricula, nombre_perfil y nivel_riesgo
    que ResultadoResumen/ResultadoRead requieren.
    """
    alumno = db.query(Alumno).filter_by(id_alumno=resultado.id_alumno).first()
    perfil = (
        db.query(PerfilPsicologico).filter_by(id_perfil=resultado.id_perfil).first()
        if resultado.id_perfil else None
    )
    data = {
        **resultado.__dict__,
        "nombre_alumno":    alumno.nombre_completo if alumno else "—",
        "codigo_matricula": alumno.codigo_matricula if alumno else "—",
        "nombre_perfil":    perfil.nombre_perfil   if perfil  else None,
        "nivel_riesgo":     perfil.nivel_riesgo    if perfil  else None,
    }
    data.pop("_sa_instance_state", None)
    return data


@router.get("/tamizaje/{id_tamizaje}", response_model=list[ResultadoResumen])
def listar_resultados_por_tamizaje(
    id_tamizaje: int,
    db: Session = Depends(get_db),
):
    """
    Lista todos los resultados de un tamizaje.
    Vista compacta para el panel de la psicóloga.
    """
    resultados = (
        db.query(ResultadoTamizaje)
        .filter_by(id_tamizaje=id_tamizaje)
        .order_by(ResultadoTamizaje.fecha_calculo.desc())
        .all()
    )
    return [ResultadoResumen(**_enriquecer(r, db)) for r in resultados]


@router.get("/{id_resultado}", response_model=ResultadoRead)
def obtener_resultado(id_resultado: int, db: Session = Depends(get_db)):
    """Devuelve el perfil completo con interpretación IA si está disponible."""
    resultado = db.query(ResultadoTamizaje).filter_by(
        id_resultado=id_resultado
    ).first()
    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado no encontrado.")
    return ResultadoRead(**_enriquecer(resultado, db))


@router.post("/interpretar-ia", response_model=ResultadoRead)
def interpretar_con_ia(
    body: SolicitudInterpretacionIA,
    db: Session = Depends(get_db),
):
    """
    Genera la interpretación IA bajo demanda para perfiles de monitoreo
    (Colérico, Sentimental) que no la reciben automáticamente.
    """
    resultado = solicitar_interpretacion_ia(body.id_resultado, db)
    db.commit()
    db.refresh(resultado)
    return ResultadoRead(**_enriquecer(resultado, db))