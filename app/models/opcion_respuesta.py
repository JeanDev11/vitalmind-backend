from sqlalchemy import Column, Integer, String, SmallInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class OpcionRespuesta(Base):
    __tablename__ = "opcion_respuesta"

    id_opcion      = Column(Integer, primary_key=True, autoincrement=True)
    id_pregunta    = Column(Integer, ForeignKey("pregunta.id_pregunta"), nullable=False)
    texto_opcion   = Column(String(200), nullable=False)
    valor_numerico = Column(Numeric(5, 2), nullable=False)
    orden          = Column(SmallInteger, nullable=True)

    # Relaciones
    pregunta       = relationship("Pregunta",     back_populates="opciones")
    respuestas     = relationship("RespuestaItem", back_populates="opcion_seleccionada")