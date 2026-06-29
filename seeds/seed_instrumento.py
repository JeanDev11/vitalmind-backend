from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.instrumento import Instrumento


def seed_instrumento(db: Session) -> int:
    """
    Retorna el id_instrumento creado para ser usado por los seeds dependientes.
    Si ya existe, retorna el id existente sin duplicar.
    """
    existente = db.query(Instrumento).filter_by(
        nombre="Cuestionario Caracterológico de Gastón Berger"
    ).first()

    if existente:
        print(f"[SKIP] Instrumento ya existe — id={existente.id_instrumento}")
        return existente.id_instrumento

    instrumento = Instrumento(
        nombre="Cuestionario Caracterológico de Gastón Berger",
        descripcion=(
            "Adaptación digitalizada de Luis Alberto Vicuña Peri. "
            "Evalúa tres dimensiones caracterológicas (Emotividad, Actividad y Resonancia) "
            "mediante 30 ítems dicotómicos, clasificando al evaluado en uno de 8 perfiles temperamentales."
        ),
        version="Vicuña Peri — Adaptación Digital",
        tipo_calificacion="calculo_interno",
        activo=True,
    )
    db.add(instrumento)
    db.flush()  # Obtener el id sin cerrar la transacción

    print(f"[OK] Instrumento creado — id={instrumento.id_instrumento}")
    return instrumento.id_instrumento


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_instrumento(db)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()