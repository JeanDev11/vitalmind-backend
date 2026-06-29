from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.perfil_psicologico import PerfilPsicologico
from seeds.seed_instrumento import seed_instrumento

# ---------------------------------------------------------------------------
# Matriz de Vicuña Peri — 8 perfiles caracterológicos
# Umbrales: E≥54 → Emotivo | A≥52 → Activo | R≥52 → Secundario
# Rango posible por dimensión: [10, 90]
# nivel_riesgo: critico | monitoreo | normal
# ---------------------------------------------------------------------------

PERFILES_BERGER = [
    {
        "nombre_perfil": "Pasional",
        "codigo_tecnico": "E-A-S",
        "descripcion_base": (
            "Emotivo, Activo y Secundario. Perfil de alta energía emocional canalizada "
            "en acción sostenida. Orientado a metas de largo plazo con gran capacidad "
            "de trabajo y compromiso. Tiende a la perfección y puede volverse rígido."
        ),
        "puntaje_min_e": 54.00, "puntaje_max_e": 90.00,
        "puntaje_min_a": 52.00, "puntaje_max_a": 90.00,
        "puntaje_min_r": 52.00, "puntaje_max_r": 90.00,
        "nivel_riesgo": "normal",
        "alerta_cita": False,
    },
    {
        "nombre_perfil": "Colérico",
        "codigo_tecnico": "E-A-P",
        "descripcion_base": (
            "Emotivo, Activo y Primario. Alta reactividad emocional con acción inmediata. "
            "Emprendedor e impulsivo. Puede tener dificultades para sostener compromisos "
            "a largo plazo. Propenso a conflictos interpersonales por baja tolerancia a "
            "la frustración."
        ),
        "puntaje_min_e": 54.00, "puntaje_max_e": 90.00,
        "puntaje_min_a": 52.00, "puntaje_max_a": 90.00,
        "puntaje_min_r": 10.00, "puntaje_max_r": 51.00,
        "nivel_riesgo": "monitoreo",
        "alerta_cita": False,
    },
    {
        "nombre_perfil": "Sentimental",
        "codigo_tecnico": "E-nA-S",
        "descripcion_base": (
            "Emotivo, No Activo y Secundario. Alta sensibilidad emocional con tendencia "
            "a la introspección y la rumia. Puede presentar bloqueos para la acción "
            "pese a tener claridad sobre sus metas. Susceptible a estados depresivos "
            "prolongados si no recibe acompañamiento."
        ),
        "puntaje_min_e": 54.00, "puntaje_max_e": 90.00,
        "puntaje_min_a": 10.00, "puntaje_max_a": 51.00,
        "puntaje_min_r": 52.00, "puntaje_max_r": 90.00,
        "nivel_riesgo": "monitoreo",
        "alerta_cita": False,
    },
    {
        "nombre_perfil": "Nervioso",
        "codigo_tecnico": "E-nA-P",
        "descripcion_base": (
            "Emotivo, No Activo y Primario. Perfil de mayor vulnerabilidad psicológica. "
            "Alta reactividad emocional sin canal de acción ni reflexión sostenida. "
            "Frecuentemente asociado a cuadros de ansiedad, baja tolerancia al estrés "
            "académico y riesgo de deserción. Requiere intervención prioritaria."
        ),
        "puntaje_min_e": 54.00, "puntaje_max_e": 90.00,
        "puntaje_min_a": 10.00, "puntaje_max_a": 51.00,
        "puntaje_min_r": 10.00, "puntaje_max_r": 51.00,
        "nivel_riesgo": "critico",
        "alerta_cita": True,
    },
    {
        "nombre_perfil": "Flemático",
        "codigo_tecnico": "nE-A-S",
        "descripcion_base": (
            "No Emotivo, Activo y Secundario. Perfil de alta estabilidad emocional y "
            "rendimiento constante. Metódico, reflexivo y persistente. Bajo perfil social "
            "pero alto rendimiento individual. Perfil académico favorable."
        ),
        "puntaje_min_e": 10.00, "puntaje_max_e": 53.00,
        "puntaje_min_a": 52.00, "puntaje_max_a": 90.00,
        "puntaje_min_r": 52.00, "puntaje_max_r": 90.00,
        "nivel_riesgo": "normal",
        "alerta_cita": False,
    },
    {
        "nombre_perfil": "Sanguíneo",
        "codigo_tecnico": "nE-A-P",
        "descripcion_base": (
            "No Emotivo, Activo y Primario. Sociable, adaptable y orientado al presente. "
            "Alta capacidad de relacionamiento pero baja profundidad en compromisos. "
            "Tendencia a la dispersión académica por búsqueda constante de novedad."
        ),
        "puntaje_min_e": 10.00, "puntaje_max_e": 53.00,
        "puntaje_min_a": 52.00, "puntaje_max_a": 90.00,
        "puntaje_min_r": 10.00, "puntaje_max_r": 51.00,
        "nivel_riesgo": "normal",
        "alerta_cita": False,
    },
    {
        "nombre_perfil": "Apático",
        "codigo_tecnico": "nE-nA-S",
        "descripcion_base": (
            "No Emotivo, No Activo y Secundario. Perfil de baja reactividad general. "
            "Tendencia al aislamiento y la pasividad. Puede pasar desapercibido en "
            "entornos grupales. El riesgo principal es la invisibilidad del deterioro "
            "académico hasta etapas avanzadas."
        ),
        "puntaje_min_e": 10.00, "puntaje_max_e": 53.00,
        "puntaje_min_a": 10.00, "puntaje_max_a": 51.00,
        "puntaje_min_r": 52.00, "puntaje_max_r": 90.00,
        "nivel_riesgo": "normal",
        "alerta_cita": False,
    },
    {
        "nombre_perfil": "Amorfo",
        "codigo_tecnico": "nE-nA-P",
        "descripcion_base": (
            "No Emotivo, No Activo y Primario. Perfil de mínima activación general. "
            "Baja iniciativa, escasa planificación y tendencia a la inercia. En contextos "
            "de alta demanda académica como ingeniería puede derivar en abandono silencioso."
        ),
        "puntaje_min_e": 10.00, "puntaje_max_e": 53.00,
        "puntaje_min_a": 10.00, "puntaje_max_a": 51.00,
        "puntaje_min_r": 10.00, "puntaje_max_r": 51.00,
        "nivel_riesgo": "normal",
        "alerta_cita": False,
    },
]


def seed_perfiles(db: Session, id_instrumento: int) -> None:
    existente = db.query(PerfilPsicologico).filter_by(
        id_instrumento=id_instrumento
    ).first()

    if existente:
        print("[SKIP] Perfiles ya existen para este instrumento.")
        return

    for data in PERFILES_BERGER:
        perfil = PerfilPsicologico(
            id_instrumento=id_instrumento,
            nombre_perfil=data["nombre_perfil"],
            descripcion_base=data["descripcion_base"],
            # puntaje_min y puntaje_max se usan como referencia del rango total.
            # La clasificación real usa los tres puntajes dimensionales
            # en el algoritmo berger.py — no un puntaje_total único.
            puntaje_min=data["puntaje_min_e"],
            puntaje_max=data["puntaje_max_e"],
            nivel_riesgo=data["nivel_riesgo"],
        )
        db.add(perfil)

    print(f"[OK] 8 perfiles caracterológicos creados para instrumento id={id_instrumento}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        id_instrumento = seed_instrumento(db)
        seed_perfiles(db, id_instrumento)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()