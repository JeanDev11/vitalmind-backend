from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Contraseñas
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT — exclusivo para el Personal (psicóloga / administrador)
# Los alumnos NO reciben JWT; su credencial es el token de negocio.
# ---------------------------------------------------------------------------

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Retorna el payload si el token es válido.
    Retorna None si el token es inválido o expirado.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Token de negocio — para el acceso efímero del alumno al cuestionario
# ---------------------------------------------------------------------------

import hashlib
import secrets


def generate_raw_token() -> str:
    """Genera un token aleatorio de 64 caracteres en texto plano."""
    return secrets.token_urlsafe(48)


def hash_token(raw_token: str) -> str:
    """SHA-256 del token en texto plano. Solo el hash se persiste en BD."""
    return hashlib.sha256(raw_token.encode()).hexdigest()