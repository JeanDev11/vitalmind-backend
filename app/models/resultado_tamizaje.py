from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ResultadoTamizaje(Base):
    __tablename__ = "resultado_tamizaje"

    id_resultado        = Column(Integer, primary_key=True, autoincrement=True)
    id_sesion           = Column(Integer, ForeignKey("sesion_respuesta.id_sesion"), unique=True, nullable=False)
    id_alumno           = Column(Integer, ForeignKey("alumno.id_alumno"), nullable=False)
    id_tamizaje         = Column(Integer, ForeignKey("tamizaje.id_tamizaje"), nullable=False)
    id_perfil           = Column(Integer, ForeignKey("perfil_psicologico.id_perfil"), nullable=True)

    # Puntajes dimensionales explícitos (Berger)
    puntaje_emotividad  = Column(Numeric(5, 2), nullable=True)
    puntaje_actividad   = Column(Numeric(5, 2), nullable=True)
    puntaje_resonancia  = Column(Numeric(5, 2), nullable=True)
    puntaje_total       = Column(Numeric(6, 2), nullable=True)

    # Alerta específica por Emotividad alta (E > 75)
    alerta_emotividad_alta = Column(String(5), default="false")

    # Interpretación IA en tres niveles
    ia_diagnostico      = Column(Text, nullable=True)
    ia_caracteristicas  = Column(Text, nullable=True)
    ia_recomendaciones  = Column(Text, nullable=True)

    estado_calculo      = Column(String(20), default="pendiente")
    # pendiente | completado | error
    fecha_calculo       = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    sesion   = relationship("SesionRespuesta",  back_populates="resultado")
    alumno   = relationship("Alumno",           back_populates="resultados")
    tamizaje = relationship("Tamizaje",         back_populates="resultados")
    perfil   = relationship("PerfilPsicologico", back_populates="resultados")
    citas    = relationship("Cita",             back_populates="resultado_origen")