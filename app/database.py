from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # Verifica conexión antes de usarla (importante en Neon)
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


# Dependencia inyectable en los routers de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()