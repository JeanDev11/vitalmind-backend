from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.personal import Personal
from app.utils.security import hash_password


def seed_personal():
    db: Session = SessionLocal()

    usuarios = [
        {
            "nombre_completo": "Admin VitalMind",
            "email": "admin@vitalmind.pe",
            "password": "admin123*",
            "rol": "administrador",
        },
        {
            "nombre_completo": "Martha Zegarra",
            "email": "psicologia@unayoe.edu.pe",
            "password": "psicologia123*",
            "rol": "psicologa",
        },
    ]

    for usuario in usuarios:
        existe = (
            db.query(Personal)
            .filter(Personal.email == usuario["email"])
            .first()
        )

        if existe:
            print(f"Ya existe {usuario['email']}")
            continue

        nuevo = Personal(
            nombre_completo=usuario["nombre_completo"],
            email=usuario["email"],
            password_hash=hash_password(usuario["password"]),
            rol=usuario["rol"],
            activo=True,
        )

        db.add(nuevo)

    db.commit()
    db.close()

    print("Usuarios creados correctamente.")


if __name__ == "__main__":
    seed_personal()