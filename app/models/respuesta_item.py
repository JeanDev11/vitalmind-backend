from sqlalchemy import Column, Integer, Text, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class RespuestaItem(Base):
    __tablename__ = "respuesta_item"
    __table_args__ = (
        UniqueConstraint("id_sesion", "id_pregunta", name="uq_respuesta_sesion_pregunta"),
    )

    id_respuesta         = Column(Integer, primary_key=True, autoincrement=True)
    id_sesion            = Column(Integer, ForeignKey("sesion_respuesta.id_sesion"), nullable=False)
    id_pregunta          = Column(Integer, ForeignKey("pregunta.id_pregunta"), nullable=False)
    id_opcion_seleccionada = Column(Integer, ForeignKey("opcion_respuesta.id_opcion"), nullable=True)
    valor_texto          = Column(Text, nullable=True)
    valor_numerico       = Column(Numeric(5, 2), nullable=True)

    # Relaciones
    sesion             = relationship("SesionRespuesta", back_populates="items")
    pregunta           = relationship("Pregunta",        back_populates="respuestas")
    opcion_seleccionada = relationship("OpcionRespuesta", back_populates="respuestas")