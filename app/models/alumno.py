from sqlalchemy import Column, Integer, String, SmallInteger
from sqlalchemy.orm import relationship
from app.database import Base


class Alumno(Base):
    __tablename__ = "alumno"

    id_alumno           = Column(Integer, primary_key=True, autoincrement=True)
    codigo_matricula    = Column(String(20), unique=True, nullable=False)
    dni                 = Column(String(8), unique=True, nullable=False)
    nombre_completo     = Column(String(200), nullable=False)
    email_institucional = Column(String(150), unique=True, nullable=False)
    anio_ingreso        = Column(SmallInteger, nullable=True)
    ciclo_actual        = Column(SmallInteger, nullable=True)
    estado              = Column(String(20), default="activo")
    # activo | inactivo | desertor | egresado

    # Relaciones
    tokens          = relationship("TokenAcceso",      back_populates="alumno")
    sesiones        = relationship("SesionRespuesta",  back_populates="alumno")
    resultados      = relationship("ResultadoTamizaje", back_populates="alumno")
    citas           = relationship("Cita",             back_populates="alumno")
    historia        = relationship("HistoriaClinica",  back_populates="alumno", uselist=False)