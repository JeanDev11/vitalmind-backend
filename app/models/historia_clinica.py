# app/models/historia_clinica.py — versión corregida

from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class HistoriaClinica(Base):
    __tablename__ = "historia_clinica"

    id_hc                = Column(Integer, primary_key=True, autoincrement=True)
    id_alumno            = Column(Integer, ForeignKey("alumno.id_alumno"), unique=True, nullable=False)
    id_personal_apertura = Column(Integer, ForeignKey("personal.id_personal"), nullable=False)
    fecha_apertura       = Column(Date, nullable=False)
    estado               = Column(String(20), default="activa")
    # activa | cerrada | derivada
    observaciones        = Column(Text, nullable=True)

    # Relaciones
    alumno            = relationship("Alumno",    foreign_keys=[id_alumno],            back_populates="historia")
    personal_apertura = relationship("Personal",  foreign_keys=[id_personal_apertura], back_populates="historias")