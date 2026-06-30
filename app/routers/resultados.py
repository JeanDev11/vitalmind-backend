from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.personal import Personal
from app.models.resultado_tamizaje import ResultadoTamizaje
from app.models.alumno import Alumno
from app.models.perfil_psicologico import PerfilPsicologico
from app.schemas.resultado import ResultadoRead, ResultadoResumen, SolicitudInterpretacionIA
from app.services.resultado_service import solicitar_interpretacion_ia
from app.utils.security import get_current_personal

router = APIRouter()


@router.get("/tamizaje/{id_tamizaje}", response_model=List[ResultadoResumen])
def listar_resultados_por_tamizaje(
    id_tamizaje: int,
    nivel_riesgo: str | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """
    Panel principal de la psicóloga.
    Lista todos los resultados de un tamizaje con filtro opcional por nivel de riesgo.
    """
    query = (
        db.query(ResultadoTamizaje)
        .join(Alumno, ResultadoTamizaje.id_alumno == Alumno.id_alumno)
        .filter(ResultadoTamizaje.id_tamizaje == id_tamizaje)
    )

    if nivel_riesgo:
        query = query.join(
            PerfilPsicologico,
            ResultadoTamizaje.id_perfil == PerfilPsicologico.id_perfil,
        ).filter(PerfilPsicologico.nivel_riesgo == nivel_riesgo)

    resultados = query.all()

    return [
        ResultadoResumen(
            id_resultado=r.id_resultado,
            id_alumno=r.id_alumno,
            nombre_alumno=r.alumno.nombre_completo,
            codigo_matricula=r.alumno.codigo_matricula,
            nombre_perfil=r.perfil.nombre_perfil if r.perfil else None,
            nivel_riesgo=r.perfil.nivel_riesgo if r.perfil else None,
            puntaje_emotividad=float(r.puntaje_emotividad) if r.puntaje_emotividad else None,
            puntaje_actividad=float(r.puntaje_actividad) if r.puntaje_actividad else None,
            puntaje_resonancia=float(r.puntaje_resonancia) if r.puntaje_resonancia else None,
            alerta_emotividad_alta=r.alerta_emotividad_alta,
            estado_calculo=r.estado_calculo,
            fecha_calculo=r.fecha_calculo,
        )
        for r in resultados
    ]


@router.get("/{id_resultado}", response_model=ResultadoRead)
def obtener_resultado(
    id_resultado: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """Perfil completo de un alumno incluyendo interpretación IA si está disponible."""
    r = db.query(ResultadoTamizaje).filter_by(id_resultado=id_resultado).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resultado no encontrado.")

    return ResultadoRead(
        id_resultado=r.id_resultado,
        id_alumno=r.id_alumno,
        nombre_alumno=r.alumno.nombre_completo,
        codigo_matricula=r.alumno.codigo_matricula,
        id_tamizaje=r.id_tamizaje,
        nombre_perfil=r.perfil.nombre_perfil if r.perfil else None,
        nivel_riesgo=r.perfil.nivel_riesgo if r.perfil else None,
        puntaje_emotividad=float(r.puntaje_emotividad) if r.puntaje_emotividad else None,
        puntaje_actividad=float(r.puntaje_actividad) if r.puntaje_actividad else None,
        puntaje_resonancia=float(r.puntaje_resonancia) if r.puntaje_resonancia else None,
        puntaje_total=float(r.puntaje_total) if r.puntaje_total else None,
        alerta_emotividad_alta=r.alerta_emotividad_alta,
        estado_calculo=r.estado_calculo,
        fecha_calculo=r.fecha_calculo,
        ia_diagnostico=r.ia_diagnostico,
        ia_caracteristicas=r.ia_caracteristicas,
        ia_recomendaciones=r.ia_recomendaciones,
    )


@router.post("/interpretar-ia", response_model=ResultadoRead)
def interpretar_con_ia(
    data: SolicitudInterpretacionIA,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_personal),
):
    """
    Genera interpretación IA bajo demanda para perfiles de monitoreo
    (Colérico, Sentimental) que no la reciben automáticamente.
    """
    resultado = solicitar_interpretacion_ia(data.id_resultado, db)
    db.commit()
    db.refresh(resultado)

    r = resultado
    return ResultadoRead(
        id_resultado=r.id_resultado,
        id_alumno=r.id_alumno,
        nombre_alumno=r.alumno.nombre_completo,
        codigo_matricula=r.alumno.codigo_matricula,
        id_tamizaje=r.id_tamizaje,
        nombre_perfil=r.perfil.nombre_perfil if r.perfil else None,
        nivel_riesgo=r.perfil.nivel_riesgo if r.perfil else None,
        puntaje_emotividad=float(r.puntaje_emotividad) if r.puntaje_emotividad else None,
        puntaje_actividad=float(r.puntaje_actividad) if r.puntaje_actividad else None,
        puntaje_resonancia=float(r.puntaje_resonancia) if r.puntaje_resonancia else None,
        puntaje_total=float(r.puntaje_total) if r.puntaje_total else None,
        alerta_emotividad_alta=r.alerta_emotividad_alta,
        estado_calculo=r.estado_calculo,
        fecha_calculo=r.fecha_calculo,
        ia_diagnostico=r.ia_diagnostico,
        ia_caracteristicas=r.ia_caracteristicas,
        ia_recomendaciones=r.ia_recomendaciones,
    )