from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Instrumento(Base):
    __tablename__ = "instrumento"

    id_instrumento   = Column(Integer, primary_key=True, autoincrement=True)
    nombre           = Column(String(150), nullable=False)
    descripcion      = Column(Text, nullable=True)
    version          = Column(String(100), nullable=True)
    tipo_calificacion = Column(String(50), nullable=False)
    # calculo_interno | api_ia | mixto
    activo           = Column(Boolean, default=True)

    # Relaciones
    preguntas        = relationship("Pregunta",          back_populates="instrumento")
    perfiles         = relationship("PerfilPsicologico", back_populates="instrumento")
    tamizajes        = relationship("Tamizaje",          back_populates="instrumento")