from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Template

from app.core.config import settings
from app.core import security

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import logging

logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str


def send_email(
    *,
    email_to: str,
    email_data: EmailData,
) -> None:
    assert settings.emails_enabled, "Email sending is not enabled in settings"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = email_data.subject
    msg["From"] = settings.EMAILS_FROM_EMAIL
    msg["To"] = email_to

    html_part = MIMEText(email_data.html_content, "html")
    msg.attach(html_part)

    try:
        logger.info(f"Conectando a SMTP {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            logger.info("Autenticando en SMTP...")
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            logger.info(f"Enviando correo a {email_to}...")
            server.sendmail(settings.EMAILS_FROM_EMAIL, email_to, msg.as_string())
            logger.info("✅ Correo enviado exitosamente.")
    except Exception as e:
        logger.error(f"❌ Error al enviar correo: {e}")
        raise


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account created {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email_to": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)

def generate_password_reset_email(
    email_to: str, token: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password reset request"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="password_reset.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "email_to": email_to,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text(encoding="utf-8")
    html_content = Template(template_str).render(context)
    return html_content