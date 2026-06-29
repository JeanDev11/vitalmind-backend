from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Tamizaje(Base):
    __tablename__ = "tamizaje"

    id_tamizaje           = Column(Integer, primary_key=True, autoincrement=True)
    id_personal_creador   = Column(Integer, ForeignKey("personal.id_personal"), nullable=False)
    id_instrumento        = Column(Integer, ForeignKey("instrumento.id_instrumento"), nullable=False)
    nombre                = Column(String(200), nullable=False)
    descripcion           = Column(Text, nullable=True)
    fecha_creacion        = Column(DateTime(timezone=True), server_default=func.now())
    fecha_limite_respuesta = Column(DateTime(timezone=True), nullable=False)
    estado                = Column(String(20), default="borrador")
    # borrador | activo | cerrado | anulado

    # Relaciones
    creador       = relationship("Personal",       back_populates="tamizajes")
    instrumento   = relationship("Instrumento",    back_populates="tamizajes")
    tokens        = relationship("TokenAcceso",    back_populates="tamizaje")
    sesiones      = relationship("SesionRespuesta", back_populates="tamizaje")
    resultados    = relationship("ResultadoTamizaje", back_populates="tamizaje")