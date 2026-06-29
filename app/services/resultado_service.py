from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.sesion_respuesta import SesionRespuesta
from app.models.resultado_tamizaje import ResultadoTamizaje
from app.models.respuesta_item import RespuestaItem
from app.models.opcion_respuesta import OpcionRespuesta
from app.models.instrumento import Instrumento
from app.schemas.sesion_respuesta import RespuestaEnvioRequest
from app.services.calificacion.berger import CalculadorBergerInterno
from app.services.calificacion.ia_gemini import CalculadorViaIA
from app.services.calificacion.interface import ICalculadorPerfil


def _seleccionar_calculador(tipo_calificacion: str) -> ICalculadorPerfil:
    if tipo_calificacion == "calculo_interno":
        return CalculadorBergerInterno()
    elif tipo_calificacion in ("api_ia", "mixto"):
        return CalculadorViaIA()
    raise ValueError(f"Tipo de calificación no soportado: {tipo_calificacion}")


def persistir_respuestas_y_calcular(
    sesion: SesionRespuesta,
    payload: RespuestaEnvioRequest,
    db: Session,
) -> ResultadoTamizaje:
    """
    Ejecuta el flujo atómico de envío del cuestionario (RN-03):
    1. Persiste cada RespuestaItem.
    2. Marca la sesión como enviada.
    3. Marca el token como usado.
    4. Calcula el perfil.
    5. Persiste el ResultadoTamizaje.
    Todo ocurre en la misma transacción — el caller hace commit o rollback.
    """
    if sesion.estado == "enviada":
        raise HTTPException(
            status_code=400,
            detail="Este cuestionario ya fue enviado y no puede modificarse.",
        )

    # Paso 1 — Persistir respuestas individuales
    for item_data in payload.respuestas:
        item = RespuestaItem(
            id_sesion=sesion.id_sesion,
            id_pregunta=item_data.id_pregunta,
            id_opcion_seleccionada=item_data.id_opcion_seleccionada,
            valor_texto=item_data.valor_texto,
        )
        db.add(item)

    db.flush()

    # Paso 2 — Marcar sesión como enviada
    sesion.estado = "enviada"
    sesion.fecha_envio = datetime.now(timezone.utc)

    # Paso 3 — Marcar token como usado
    sesion.token.estado = "usado"
    sesion.token.fecha_uso = datetime.now(timezone.utc)

    db.flush()

    # Paso 4 — Seleccionar calculador según instrumento
    instrumento = db.query(Instrumento).filter_by(
        id_instrumento=sesion.tamizaje.id_instrumento
    ).first()

    calculador = _seleccionar_calculador(instrumento.tipo_calificacion)

    try:
        datos_resultado = calculador.calcular(sesion, db)
        estado_calculo = "completado"
    except Exception as e:
        print(f"[ERROR] Cálculo de perfil fallido para sesión {sesion.id_sesion}: {e}")
        datos_resultado = {
            "puntaje_emotividad": None, "puntaje_actividad": None,
            "puntaje_resonancia": None, "puntaje_total": None,
            "id_perfil": None, "alerta_emotividad_alta": "false",
            "ia_diagnostico": None, "ia_caracteristicas": None,
            "ia_recomendaciones": None,
        }
        estado_calculo = "error"

    # Paso 5 — Persistir resultado
    resultado = ResultadoTamizaje(
        id_sesion=sesion.id_sesion,
        id_alumno=sesion.id_alumno,
        id_tamizaje=sesion.id_tamizaje,
        id_perfil=datos_resultado["id_perfil"],
        puntaje_emotividad=datos_resultado["puntaje_emotividad"],
        puntaje_actividad=datos_resultado["puntaje_actividad"],
        puntaje_resonancia=datos_resultado["puntaje_resonancia"],
        puntaje_total=datos_resultado["puntaje_total"],
        alerta_emotividad_alta=datos_resultado["alerta_emotividad_alta"],
        ia_diagnostico=datos_resultado["ia_diagnostico"],
        ia_caracteristicas=datos_resultado["ia_caracteristicas"],
        ia_recomendaciones=datos_resultado["ia_recomendaciones"],
        estado_calculo=estado_calculo,
        fecha_calculo=datetime.now(timezone.utc),
    )
    db.add(resultado)
    db.flush()

    return resultado


def solicitar_interpretacion_ia(
    id_resultado: int,
    db: Session,
) -> ResultadoTamizaje:
    """
    Genera la interpretación IA bajo demanda para perfiles
    de monitoreo secundario (Colérico, Sentimental).
    """
    resultado = db.query(ResultadoTamizaje).filter_by(
        id_resultado=id_resultado
    ).first()

    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado no encontrado.")

    if resultado.ia_diagnostico:
        raise HTTPException(
            status_code=400,
            detail="Este resultado ya tiene interpretación IA generada.",
        )

    sesion = resultado.sesion
    instrumento = sesion.tamizaje.instrumento
    calculador = CalculadorViaIA()

    datos = calculador.calcular(sesion, db)
    resultado.ia_diagnostico     = datos.get("ia_diagnostico")
    resultado.ia_caracteristicas = datos.get("ia_caracteristicas")
    resultado.ia_recomendaciones = datos.get("ia_recomendaciones")

    db.flush()
    return resultado