from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.personal import Personal
from app.schemas.auth import LoginRequest, TokenResponse
from app.utils.security import verify_password, create_access_token


def login(request: LoginRequest, db: Session) -> TokenResponse:
    personal = db.query(Personal).filter_by(email=request.email).first()

    if not personal or not verify_password(request.password, personal.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
        )

    if not personal.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta inactiva. Contacte al administrador.",
        )

    access_token = create_access_token(data={
        "sub": str(personal.id_personal),
        "rol": personal.rol,
    })

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        nombre_completo=personal.nombre_completo,
        rol=personal.rol,
    )


def get_personal_activo(id_personal: int, db: Session) -> Personal:
    """Dependencia reutilizable para verificar que el personal existe y está activo."""
    personal = db.query(Personal).filter_by(
        id_personal=id_personal, activo=True
    ).first()

    if not personal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal no encontrado o inactivo.",
        )
    return personal