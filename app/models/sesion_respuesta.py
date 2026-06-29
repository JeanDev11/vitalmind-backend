from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SesionRespuesta(Base):
    __tablename__ = "sesion_respuesta"

    id_sesion   = Column(Integer, primary_key=True, autoincrement=True)
    id_token    = Column(Integer, ForeignKey("token_acceso.id_token"), unique=True, nullable=False)
    id_tamizaje = Column(Integer, ForeignKey("tamizaje.id_tamizaje"), nullable=False)
    id_alumno   = Column(Integer, ForeignKey("alumno.id_alumno"), nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_envio  = Column(DateTime(timezone=True), nullable=True)
    estado       = Column(String(20), default="en_progreso")
    # en_progreso | enviada

    # Relaciones
    token       = relationship("TokenAcceso",      back_populates="sesion")
    tamizaje    = relationship("Tamizaje",         back_populates="sesiones")
    alumno      = relationship("Alumno",           back_populates="sesiones")
    items       = relationship("RespuestaItem",    back_populates="sesion")
    resultado   = relationship("ResultadoTamizaje", back_populates="sesion", uselist=False)