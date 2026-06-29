import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.config import get_settings

settings = get_settings()


def _build_connection() -> smtplib.SMTP:
    server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
    server.ehlo()
    server.starttls()
    server.login(settings.smtp_user, settings.smtp_password)
    return server


def _send(to_email: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.email_from
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with _build_connection() as server:
        server.sendmail(settings.smtp_user, to_email, msg.as_string())


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def _template_token_cuestionario(
    nombre_alumno: str,
    nombre_tamizaje: str,
    enlace: str,
    fecha_limite: str,
) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2E6DA4;">VitalMind — FISI UNMSM</h2>
        <p>Hola <strong>{nombre_alumno}</strong>,</p>
        <p>
          Has sido convocado/a a completar el siguiente cuestionario psicopedagógico:
          <strong>{nombre_tamizaje}</strong>.
        </p>
        <p>
          Haz clic en el botón para acceder. El enlace es de <strong>un solo uso</strong>
          y expira el <strong>{fecha_limite}</strong>.
        </p>
        <p style="text-align: center; margin: 32px 0;">
          <a href="{enlace}"
             style="background-color: #2E6DA4; color: white; padding: 12px 24px;
                    text-decoration: none; border-radius: 4px; font-size: 16px;">
            Completar cuestionario
          </a>
        </p>
        <p style="font-size: 12px; color: #888;">
          Si no esperabas este mensaje, ignóralo. No compartas este enlace con nadie.
          Tu información es confidencial y será manejada exclusivamente por el personal de UNAYOE.
        </p>
      </body>
    </html>
    """


def _template_confirmacion_cita(
    nombre_alumno: str,
    fecha: str,
    hora: str,
    modalidad: Optional[str] = None,
) -> str:
    detalle_modalidad = f"<p>Modalidad: <strong>{modalidad}</strong></p>" if modalidad else ""
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2E6DA4;">VitalMind — FISI UNMSM</h2>
        <p>Hola <strong>{nombre_alumno}</strong>,</p>
        <p>
          Tu cita con la Unidad de Apoyo y Orientación al Estudiante (UNAYOE)
          ha sido programada.
        </p>
        <p>Fecha: <strong>{fecha}</strong></p>
        <p>Hora: <strong>{hora}</strong></p>
        {detalle_modalidad}
        <p style="font-size: 12px; color: #888;">
          Si tienes alguna consulta, comunícate directamente con UNAYOE.
          Esta cita es confidencial.
        </p>
      </body>
    </html>
    """


# ---------------------------------------------------------------------------
# Funciones públicas
# ---------------------------------------------------------------------------

def enviar_token_cuestionario(
    to_email: str,
    nombre_alumno: str,
    nombre_tamizaje: str,
    raw_token: str,
    fecha_limite: str,
    base_url: str,
) -> None:
    """
    Envía el enlace de acceso al cuestionario al alumno.
    El enlace contiene el token en texto plano; el backend hashea al recibirlo.
    """
    enlace = f"{base_url}/cuestionario?token={raw_token}"
    html = _template_token_cuestionario(
        nombre_alumno=nombre_alumno,
        nombre_tamizaje=nombre_tamizaje,
        enlace=enlace,
        fecha_limite=fecha_limite,
    )
    _send(
        to_email=to_email,
        subject=f"VitalMind — Cuestionario: {nombre_tamizaje}",
        html_body=html,
    )


def enviar_confirmacion_cita(
    to_email: str,
    nombre_alumno: str,
    fecha: str,
    hora: str,
    modalidad: Optional[str] = None,
) -> None:
    """Notifica al alumno que tiene una cita programada en UNAYOE."""
    html = _template_confirmacion_cita(
        nombre_alumno=nombre_alumno,
        fecha=fecha,
        hora=hora,
        modalidad=modalidad,
    )
    _send(
        to_email=to_email,
        subject="VitalMind — Cita programada en UNAYOE",
        html_body=html,
    )