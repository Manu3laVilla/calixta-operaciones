from __future__ import annotations

import base64
import smtplib
from datetime import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd

from utils.settings import get_env


def _smtp_config() -> dict[str, str | int]:
    """Lee SMTP en cada envío para tomar cambios recientes del .env local."""
    from dotenv import load_dotenv

    load_dotenv(override=True)
    return {
        "host": get_env("SMTP_HOST", "smtp.gmail.com"),
        "port": int(get_env("SMTP_PORT", "587")),
        "user": get_env("SMTP_USER", "").strip(),
        "password": get_env("SMTP_PASSWORD", "").strip().replace(" ", ""),
        "to": get_env("ALERT_EMAIL_TO", "calixtaa.co@gmail.com").strip(),
    }


def is_email_configured() -> bool:
    cfg = _smtp_config()
    user = str(cfg["user"])
    password = str(cfg["password"])
    recipient = str(cfg["to"])
    if not (user and password and recipient):
        return False
    password_lower = password.lower()
    if password_lower in {
        "tu_contraseña_de_aplicacion",
        "tu_contrasena_de_aplicacion",
        "xxxx xxxx xxxx xxxx",
        "changeme",
        "password",
    }:
        return False
    if password_lower.startswith("tu_") or "contrase" in password_lower:
        return False
    return True


def _smtp_login(server: smtplib.SMTP, *, user: str, password: str) -> None:
    """Autenticación SMTP compatible con contraseñas no ASCII (Gmail, etc.)."""
    credentials = f"{user}{password}"

    def _plain_utf8() -> None:
        auth = base64.b64encode(
            f"\0{user}\0{password}".encode("utf-8")
        ).decode("ascii")
        code, response = server.docmd("AUTH", f"PLAIN {auth}")
        if code != 235:
            raise smtplib.SMTPAuthenticationError(code, response)

    if all(ord(char) < 128 for char in credentials):
        server.login(user, password)
        return

    _plain_utf8()


def alert_recipient() -> str:
    recipients = resolve_alert_recipients()
    return ", ".join(recipients)


def resolve_alert_recipients(explicit: list[str] | None = None) -> list[str]:
    if explicit:
        return explicit
    try:
        from services.alert_config_service import get_active_alert_recipient_emails

        configured = get_active_alert_recipient_emails()
        if configured:
            return configured
    except Exception:
        pass
    fallback = str(_smtp_config()["to"]).strip()
    return [fallback] if fallback else []


def _build_html_table(alerts: pd.DataFrame) -> str:
    columns = [
        ("referencia", "Referencia"),
        ("nombre", "Nombre"),
        ("talla", "Talla"),
        ("color", "Color"),
        ("categoria", "Categoría"),
        ("stock", "Stock actual"),
        ("stock_minimo", "Stock mínimo"),
        ("faltante", "Faltante"),
    ]

    header = "".join(f"<th style='padding:8px;border:1px solid #ddd;'>{label}</th>" for _, label in columns)
    rows = ""
    for _, row in alerts.iterrows():
        cells = "".join(
            f"<td style='padding:8px;border:1px solid #ddd;'>{row.get(col, '')}</td>"
            for col, _ in columns
        )
        rows += f"<tr>{cells}</tr>"

    return f"""
    <table style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif;font-size:14px;">
        <thead><tr style="background:#F5F0E8;">{header}</tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """


def send_low_stock_alert(
    alerts: pd.DataFrame,
    *,
    recipients: list[str] | None = None,
) -> None:
    if alerts.empty:
        raise ValueError("No hay productos con stock bajo para notificar.")
    if not is_email_configured():
        raise ValueError(
            "Correo no configurado. Agrega SMTP_USER y SMTP_PASSWORD en el archivo .env"
        )

    targets = resolve_alert_recipients(recipients)
    if not targets:
        raise ValueError(
            "No hay destinatarios configurados. Agrega correos en Administración → Alertas por correo."
        )

    cfg = _smtp_config()
    smtp_user = str(cfg["user"])
    smtp_password = str(cfg["password"])
    smtp_host = str(cfg["host"])
    smtp_port = int(cfg["port"])

    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    count = len(alerts)
    subject = f"[Calixta] Alerta de stock bajo — {count} producto(s)"

    html_body = f"""
    <html>
    <body style="font-family:Arial,sans-serif;color:#1A1A1A;">
        <h2 style="font-weight:normal;letter-spacing:2px;">CALIXTA</h2>
        <p>Centro de Operaciones — Alerta de inventario</p>
        <p>Se detectaron <strong>{count}</strong> producto(s) con stock en o por debajo del mínimo.</p>
        <p><em>Generado el {now}</em></p>
        {_build_html_table(alerts)}
        <p style="margin-top:24px;color:#6B6560;font-size:12px;">
            Este correo fue enviado automáticamente por Calixta Centro de Operaciones.
        </p>
    </body>
    </html>
    """

    text_lines = [f"Calixta — Alerta de stock bajo ({count} productos)\n"]
    for _, row in alerts.iterrows():
        text_lines.append(
            f"- {row.get('referencia', '')} | {row.get('nombre', '')} | "
            f"Stock: {row.get('stock', 0)} / Mín: {row.get('stock_minimo', 0)}"
        )
    text_body = "\n".join(text_lines)

    message = MIMEMultipart("alternative")
    message["Subject"] = Header(subject, "utf-8")
    message["From"] = smtp_user
    message["To"] = ", ".join(targets)
    message.attach(MIMEText(text_body, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        _smtp_login(server, user=smtp_user, password=smtp_password)
        server.sendmail(smtp_user, targets, message.as_string())
