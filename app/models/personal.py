from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Personal(Base):
    __tablename__ = "personal"

    id_personal     = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String(150), nullable=False)
    email           = Column(String(150), unique=True, nullable=False)
    password_hash   = Column(String(255), nullable=False)
    rol             = Column(String(30), nullable=False)  # psicologa | administrador
    activo          = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    tamizajes       = relationship("Tamizaje",       back_populates="creador")
    disponibilidades = relationship("Disponibilidad", back_populates="personal")
    citas           = relationship("Cita",           back_populates="personal")
    historias       = relationship("HistoriaClinica", back_populates="personal_apertura")