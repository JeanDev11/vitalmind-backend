"""
Punto de entrada único para ejecutar todos los seeds en orden.
Uso: python -m seeds.run_all
"""
from app.database import SessionLocal
from seeds.seed_instrumento import seed_instrumento
from seeds.seed_preguntas import seed_preguntas
from seeds.seed_perfiles import seed_perfiles


def run_all() -> None:
    db = SessionLocal()
    try:
        print("=== VitalMind — Seed inicial ===")
        id_instrumento = seed_instrumento(db)
        seed_preguntas(db, id_instrumento)
        seed_perfiles(db, id_instrumento)
        db.commit()
        print("=== Seed completado exitosamente ===")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed fallido — rollback aplicado: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    run_all()