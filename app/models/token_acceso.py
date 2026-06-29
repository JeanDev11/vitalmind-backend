from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class TokenAcceso(Base):
    __tablename__ = "token_acceso"
    __table_args__ = (
        UniqueConstraint("id_tamizaje", "id_alumno", name="uq_token_tamizaje_alumno"),
    )

    id_token        = Column(Integer, primary_key=True, autoincrement=True)
    id_tamizaje     = Column(Integer, ForeignKey("tamizaje.id_tamizaje"), nullable=False)
    id_alumno       = Column(Integer, ForeignKey("alumno.id_alumno"), nullable=False)
    token_hash      = Column(String(255), unique=True, nullable=False)
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False)
    estado          = Column(String(20), default="pendiente")
    # pendiente | usado | expirado | anulado
    fecha_uso       = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    tamizaje        = relationship("Tamizaje",       back_populates="tokens")
    alumno          = relationship("Alumno",         back_populates="tokens")
    sesion          = relationship("SesionRespuesta", back_populates="token", uselist=False)