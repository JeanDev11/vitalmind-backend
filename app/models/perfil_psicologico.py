from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class PerfilPsicologico(Base):
    __tablename__ = "perfil_psicologico"

    id_perfil      = Column(Integer, primary_key=True, autoincrement=True)
    id_instrumento = Column(Integer, ForeignKey("instrumento.id_instrumento"), nullable=False)
    nombre_perfil  = Column(String(100), nullable=False)
    # Pasional | Colérico | Sentimental | Nervioso | Flemático | Sanguíneo | Apático | Amorfo
    descripcion_base = Column(Text, nullable=True)
    puntaje_min    = Column(Numeric(5, 2), nullable=True)
    puntaje_max    = Column(Numeric(5, 2), nullable=True)
    nivel_riesgo   = Column(String(20), nullable=True)
    # critico | monitoreo | normal

    # Relaciones
    instrumento    = relationship("Instrumento",      back_populates="perfiles")
    resultados     = relationship("ResultadoTamizaje", back_populates="perfil")