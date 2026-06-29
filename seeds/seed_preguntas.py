from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.pregunta import Pregunta
from app.models.opcion_respuesta import OpcionRespuesta
from seeds.seed_instrumento import seed_instrumento

# ---------------------------------------------------------------------------
# NOTA PARA EL EQUIPO:
#
# Este set de 30 ítems es UNA ADAPTACIÓN COMPLETAMENTE ORIGINAL, creada para
# fines de desarrollo y pruebas. NO es una copia ni traducción del
# "Cuestionario Caracterológico de Gaston Berger - Adaptación Luis A.
# Vicuña Peri", el cual está protegido por derechos de autor y requiere
# licencia para uso oficial.
#
# Se conserva, de forma intencional, la misma ESTRUCTURA funcional para que
# el sistema pueda probarse de extremo a extremo:
#   - 3 dimensiones: emotividad, actividad, resonancia (10 ítems cada una)
#   - Escala de pesos 9 / 5 / 1
#   - 28 ítems dicotómicos (2 opciones) + 2 ítems tricotómicos (3 opciones:
#     ítems 11 y 26), igual que en el diseño original del sistema.
#
# Cuando el equipo cuente con la licencia del instrumento real, este archivo
# se reemplaza por el contenido oficial SIN tocar el modelo de datos ni el
# backend: solo cambian los strings de "enunciado" y "texto_opcion".
# ---------------------------------------------------------------------------

PREGUNTAS_BERGER = [
    # -----------------------------------------------------------------------
    # DIMENSIÓN EMOTIVIDAD (ítems 1-10)
    # Opción A (alta reactividad emocional) -> peso 9
    # Opción B (baja reactividad emocional) -> peso 1
    # -----------------------------------------------------------------------
    {
        "orden": 1, "dimension": "emotividad", "tipo_respuesta": "dicotomica",
        "enunciado": "¿Cuál de estas frases te representa mejor?",
        "opciones": [
            {"texto_opcion": "Las críticas, aunque sean pequeñas, me afectan profundamente.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Las críticas rara vez me afectan, salvo que sean muy graves.",   "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 2, "dimension": "emotividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Frente a una noticia inesperada (buena o mala)...",
        "opciones": [
            {"texto_opcion": "Reacciono de inmediato y con bastante intensidad.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Reacciono de forma serena, sin mucho aspaviento.",   "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 3, "dimension": "emotividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Antes de una situación importante (examen, entrevista)...",
        "opciones": [
            {"texto_opcion": "Siento nervios e inquietud notorios en el cuerpo.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Me mantengo tranquilo, sin mayores síntomas físicos.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 4, "dimension": "emotividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Cuando veo una película o leo algo triste...",
        "opciones": [
            {"texto_opcion": "Me conmuevo con facilidad, incluso hasta las lágrimas.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Lo aprecio, pero no me genera una reacción fuerte.",     "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 5, "dimension": "emotividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Cuando algo no sale como esperaba...",
        "opciones": [
            {"texto_opcion": "Me cuesta varias horas recuperar la calma.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Lo dejo pasar y sigo con mi día sin problema.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 6, "dimension": "emotividad", "tipo_respuesta": "dicotomica",
        "enunciado": "En una discusión con alguien cercano...",
        "opciones": [
            {"texto_opcion": "Se me altera la voz y el pulso con facilidad.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Suelo mantener un tono y un pulso estables.",   "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 7, "dimension": "emotividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Ante un imprevisto de último minuto...",
        "opciones": [
            {"texto_opcion": "Me genera una sensación intensa de alarma.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Lo proceso con calma y busco una solución.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 8, "dimension": "emotividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Cuando recibo un halago o reconocimiento...",
        "opciones": [
            {"texto_opcion": "Siento una emoción fuerte que se nota en mi rostro.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Lo agradezco, pero sin mostrar mucha emoción.",       "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 9, "dimension": "emotividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Cuando tengo que hablar frente a un grupo...",
        "opciones": [
            {"texto_opcion": "Siento tensión notoria antes y durante la exposición.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Lo hago con tranquilidad, sin mucha tensión previa.",   "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 10, "dimension": "emotividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Frente a un conflicto entre amigos o familiares...",
        "opciones": [
            {"texto_opcion": "Me involucro emocionalmente aunque no sea mi conflicto.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Lo observo con cierta distancia emocional.",               "valor_numerico": 1.00, "orden": 2},
        ],
    },
    # -----------------------------------------------------------------------
    # DIMENSIÓN ACTIVIDAD (ítems 11-20)
    # Ítem 11 es el único con 3 opciones (incluye opción intermedia -> peso 5)
    # Opción activa -> peso 9 | intermedia -> peso 5 | poco activa -> peso 1
    # -----------------------------------------------------------------------
    {
        "orden": 11, "dimension": "actividad", "tipo_respuesta": "tricotomica",
        "enunciado": "Cuando surge una tarea nueva y sin instrucciones claras...",
        "opciones": [
            {"texto_opcion": "Empiezo a actuar de inmediato y ajusto sobre la marcha.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Reviso un poco la situación antes de moverme.",           "valor_numerico": 5.00, "orden": 2},
            {"texto_opcion": "Prefiero esperar instrucciones más claras antes de actuar.", "valor_numerico": 1.00, "orden": 3},
        ],
    },
    {
        "orden": 12, "dimension": "actividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Frente a un proyecto grupal...",
        "opciones": [
            {"texto_opcion": "Suelo tomar la iniciativa y proponer el primer paso.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Prefiero esperar a que otro proponga el primer paso.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 13, "dimension": "actividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Cuando tengo una idea que me entusiasma...",
        "opciones": [
            {"texto_opcion": "La pongo en marcha casi de inmediato.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "La pienso bastante antes de animarme a ejecutarla.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 14, "dimension": "actividad", "tipo_respuesta": "dicotomica",
        "enunciado": "En mi tiempo libre...",
        "opciones": [
            {"texto_opcion": "Busco actividades o planes para mantenerme ocupado.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Disfruto quedarme quieto, sin necesidad de hacer algo.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 15, "dimension": "actividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Cuando algo me sale mal en el primer intento...",
        "opciones": [
            {"texto_opcion": "Lo vuelvo a intentar enseguida, casi sin pensarlo.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Necesito un buen descanso antes de volver a intentarlo.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 16, "dimension": "actividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Frente a una larga lista de pendientes...",
        "opciones": [
            {"texto_opcion": "Empiezo a resolverlos uno por uno sin demorarme en pensarlo.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Me cuesta arrancar y suelo postergar el inicio.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 17, "dimension": "actividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Durante una reunión o clase larga...",
        "opciones": [
            {"texto_opcion": "Me cuesta quedarme quieto, busco moverme o participar.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Puedo permanecer quieto y atento sin dificultad.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 18, "dimension": "actividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Cuando tengo varias metas pendientes...",
        "opciones": [
            {"texto_opcion": "Avanzo en varias a la vez, sin esperar a terminar una.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Prefiero terminar una antes de pensar en la siguiente.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 19, "dimension": "actividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Ante un cambio repentino de planes...",
        "opciones": [
            {"texto_opcion": "Me adapto rápido y reorganizo todo de inmediato.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Necesito tiempo antes de reorganizar mis actividades.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    {
        "orden": 20, "dimension": "actividad", "tipo_respuesta": "dicotomica",
        "enunciado": "Después de un día agotador...",
        "opciones": [
            {"texto_opcion": "Aun así, busco aprovechar algo de tiempo para hacer algo más.", "valor_numerico": 9.00, "orden": 1},
            {"texto_opcion": "Prefiero descansar por completo sin hacer nada más.", "valor_numerico": 1.00, "orden": 2},
        ],
    },
    # -----------------------------------------------------------------------
    # DIMENSIÓN RESONANCIA (ítems 21-30)
    # Reacción primaria (vive el presente, olvida rápido) -> peso 1
    # Reacción secundaria (las impresiones le duran, reflexiona en el pasado) -> peso 9
    # Ítem 26 es el único con 3 opciones (incluye opción intermedia -> peso 5)
    # -----------------------------------------------------------------------
    {
        "orden": 21, "dimension": "resonancia", "tipo_respuesta": "dicotomica",
        "enunciado": "Después de un mal momento...",
        "opciones": [
            {"texto_opcion": "Lo supero rápido y sigo con normalidad.", "valor_numerico": 1.00, "orden": 1},
            {"texto_opcion": "Sigo pensando en ello incluso días después.", "valor_numerico": 9.00, "orden": 2},
        ],
    },
    {
        "orden": 22, "dimension": "resonancia", "tipo_respuesta": "dicotomica",
        "enunciado": "Mis decisiones suelen estar más influidas por...",
        "opciones": [
            {"texto_opcion": "Lo que estoy viviendo en este momento.", "valor_numerico": 1.00, "orden": 1},
            {"texto_opcion": "Experiencias pasadas que todavía recuerdo con claridad.", "valor_numerico": 9.00, "orden": 2},
        ],
    },
    {
        "orden": 23, "dimension": "resonancia", "tipo_respuesta": "dicotomica",
        "enunciado": "Cuando alguien me decepciona...",
        "opciones": [
            {"texto_opcion": "Lo olvido con relativa facilidad al poco tiempo.", "valor_numerico": 1.00, "orden": 1},
            {"texto_opcion": "Me cuesta mucho volver a confiar como antes.", "valor_numerico": 9.00, "orden": 2},
        ],
    },
    {
        "orden": 24, "dimension": "resonancia", "tipo_respuesta": "dicotomica",
        "enunciado": "Los recuerdos de mi infancia o adolescencia...",
        "opciones": [
            {"texto_opcion": "Los tengo presentes, pero no influyen mucho en mi día a día.", "valor_numerico": 1.00, "orden": 1},
            {"texto_opcion": "Siguen influyendo bastante en cómo decido las cosas hoy.", "valor_numerico": 9.00, "orden": 2},
        ],
    },
    {
        "orden": 25, "dimension": "resonancia", "tipo_respuesta": "dicotomica",
        "enunciado": "Frente a un cambio brusco de planes...",
        "opciones": [
            {"texto_opcion": "Me adapto sin darle mayor vuelta al asunto.", "valor_numerico": 1.00, "orden": 1},
            {"texto_opcion": "Necesito procesarlo durante un buen rato antes de aceptarlo.", "valor_numerico": 9.00, "orden": 2},
        ],
    },
    {
        "orden": 26, "dimension": "resonancia", "tipo_respuesta": "tricotomica",
        "enunciado": "Cuando algo me marca emocionalmente (bueno o malo)...",
        "opciones": [
            {"texto_opcion": "Lo vivo intensamente, pero se me pasa rápido.", "valor_numerico": 1.00, "orden": 1},
            {"texto_opcion": "Me dura un tiempo moderado antes de dejarlo atrás.", "valor_numerico": 5.00, "orden": 2},
            {"texto_opcion": "Me acompaña durante mucho tiempo, casi no se borra.", "valor_numerico": 9.00, "orden": 3},
        ],
    },
    {
        "orden": 27, "dimension": "resonancia", "tipo_respuesta": "dicotomica",
        "enunciado": "Cuando reviso cómo fue mi semana...",
        "opciones": [
            {"texto_opcion": "Pienso sobre todo en lo que viene, no en lo ya pasado.", "valor_numerico": 1.00, "orden": 1},
            {"texto_opcion": "Repaso mentalmente varias veces lo que ya ocurrió.", "valor_numerico": 9.00, "orden": 2},
        ],
    },
    {
        "orden": 28, "dimension": "resonancia", "tipo_respuesta": "dicotomica",
        "enunciado": "Si cometo un error importante...",
        "opciones": [
            {"texto_opcion": "Lo corrijo y avanzo sin darle más vueltas.", "valor_numerico": 1.00, "orden": 1},
            {"texto_opcion": "Lo recuerdo por mucho tiempo, aunque ya lo haya corregido.", "valor_numerico": 9.00, "orden": 2},
        ],
    },
    {
        "orden": 29, "dimension": "resonancia", "tipo_respuesta": "dicotomica",
        "enunciado": "Mis estados de ánimo...",
        "opciones": [
            {"texto_opcion": "Cambian con facilidad según lo que pasa en el momento.", "valor_numerico": 1.00, "orden": 1},
            {"texto_opcion": "Se mantienen estables por bastante tiempo, sin cambiar tan rápido.", "valor_numerico": 9.00, "orden": 2},
        ],
    },
    {
        "orden": 30, "dimension": "resonancia", "tipo_respuesta": "dicotomica",
        "enunciado": "Cuando termina una etapa importante (un curso, un trabajo)...",
        "opciones": [
            {"texto_opcion": "Paso rápido a la siguiente, sin mirar mucho atrás.", "valor_numerico": 1.00, "orden": 1},
            {"texto_opcion": "Me quedo reflexionando bastante tiempo sobre esa etapa.", "valor_numerico": 9.00, "orden": 2},
        ],
    },
]
 
 
def seed_preguntas(db: Session, id_instrumento: int, forzar: bool = False) -> None:
    """
    Carga las preguntas y opciones de respuesta para un instrumento.
 
    Parametros
    ----------
    forzar:
        Si es True, elimina las preguntas/opciones existentes del
        instrumento antes de volver a insertarlas. Útil en desarrollo
        cuando se actualiza el contenido (enunciados, opciones, etc.)
        y se desea volver a sembrar sin tener que limpiar la BD a mano.
    """
    existente = db.query(Pregunta).filter_by(id_instrumento=id_instrumento).first()
    if existente:
        if not forzar:
            print("[SKIP] Preguntas ya existen para este instrumento.")
            return
        print("[INFO] Eliminando preguntas/opciones previas para re-seedear...")
        preguntas_previas = db.query(Pregunta).filter_by(id_instrumento=id_instrumento).all()
        for p in preguntas_previas:
            db.query(OpcionRespuesta).filter_by(id_pregunta=p.id_pregunta).delete()
        db.query(Pregunta).filter_by(id_instrumento=id_instrumento).delete()
        db.flush()
 
    for data in PREGUNTAS_BERGER:
        pregunta = Pregunta(
            id_instrumento=id_instrumento,
            orden=data["orden"],
            enunciado=data["enunciado"],
            dimension=data["dimension"],
            tipo_respuesta=data["tipo_respuesta"],
            activo=True,
        )
        db.add(pregunta)
        db.flush()
 
        for op in data["opciones"]:
            opcion = OpcionRespuesta(
                id_pregunta=pregunta.id_pregunta,
                texto_opcion=op["texto_opcion"],
                valor_numerico=op["valor_numerico"],
                orden=op["orden"],
            )
            db.add(opcion)
 
    print(f"[OK] 30 preguntas y sus opciones creadas para instrumento id={id_instrumento}")
 
 
if __name__ == "__main__":
    db = SessionLocal()
    try:
        id_instrumento = seed_instrumento(db)
        # Cambia forzar=True si ya habías corrido el seed antes y quieres
        # reemplazar el contenido.
        seed_preguntas(db, id_instrumento, forzar=True)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()