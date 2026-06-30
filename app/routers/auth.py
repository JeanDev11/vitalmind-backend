from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import login

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login_personal(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Autenticación del personal de UNAYOE.
    Retorna JWT para uso en endpoints protegidos.
    """
    return login(request, db)