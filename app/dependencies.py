from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.security import decode_access_token
from app.models.personal import Personal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Personal:
    """
    Dependencia global para todos los endpoints protegidos del Personal.
    Decodifica el JWT, verifica firma y extrae el usuario activo.
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise exc

    id_personal: str | None = payload.get("sub")
    if id_personal is None:
        raise exc

    personal = db.query(Personal).filter_by(
        id_personal=int(id_personal), activo=True
    ).first()

    if not personal:
        raise exc

    return personal


def require_rol(*roles: str):
    """
    Factoría de dependencias para restringir endpoints por rol.
    Uso: Depends(require_rol("administrador"))
    """
    def _check(current_user: Personal = Depends(get_current_user)) -> Personal:
        if current_user.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere rol: {', '.join(roles)}.",
            )
        return current_user
    return _check