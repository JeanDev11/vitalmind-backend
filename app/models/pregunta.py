from sqlalchemy import Column, Integer, String, Text, SmallInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Pregunta(Base):
    __tablename__ = "pregunta"

    id_pregunta    = Column(Integer, primary_key=True, autoincrement=True)
    id_instrumento = Column(Integer, ForeignKey("instrumento.id_instrumento"), nullable=False)
    orden          = Column(SmallInteger, nullable=False)
    enunciado      = Column(Text, nullable=False)
    dimension      = Column(String(50), nullable=True)
    # emotividad | actividad | resonancia
    tipo_respuesta = Column(String(20), nullable=False)
    # likert | si_no | escala | texto
    activo         = Column(Boolean, default=True)

    # Relaciones
    instrumento    = relationship("Instrumento",    back_populates="preguntas")
    opciones       = relationship("OpcionRespuesta", back_populates="pregunta")
    respuestas     = relationship("RespuestaItem",   back_populates="pregunta")