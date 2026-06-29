from sqlalchemy import Column, Integer, Date, Time, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Disponibilidad(Base):
    __tablename__ = "disponibilidad"
    __table_args__ = (
        UniqueConstraint("id_personal", "fecha", "hora_inicio", name="uq_slot_personal"),
    )

    id_slot     = Column(Integer, primary_key=True, autoincrement=True)
    id_personal = Column(Integer, ForeignKey("personal.id_personal"), nullable=False)
    fecha       = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin    = Column(Time, nullable=False)
    disponible  = Column(Boolean, default=True)

    # Relaciones
    personal    = relationship("Personal",  back_populates="disponibilidades")
    cita        = relationship("Cita",      back_populates="slot", uselist=False)