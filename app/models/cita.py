from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Cita(Base):
    __tablename__ = "cita"

    id_cita            = Column(Integer, primary_key=True, autoincrement=True)
    id_slot            = Column(Integer, ForeignKey("disponibilidad.id_slot"), unique=True, nullable=False)
    id_alumno          = Column(Integer, ForeignKey("alumno.id_alumno"), nullable=False)
    id_personal        = Column(Integer, ForeignKey("personal.id_personal"), nullable=False)
    id_resultado_origen = Column(Integer, ForeignKey("resultado_tamizaje.id_resultado"), nullable=True)
    motivo             = Column(Text, nullable=True)
    estado             = Column(String(20), default="programada")
    # programada | completada | cancelada | no_asistio
    notas_sesion       = Column(Text, nullable=True)
    fecha_creacion     = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    slot             = relationship("Disponibilidad",   back_populates="cita")
    alumno           = relationship("Alumno",           back_populates="citas")
    personal         = relationship("Personal",         back_populates="citas")
    resultado_origen = relationship("ResultadoTamizaje", back_populates="citas")