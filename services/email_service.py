from __future__ import annotations

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd

from app_config import ALERT_EMAIL_TO, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER


def is_email_configured() -> bool:
    return bool(SMTP_USER and SMTP_PASSWORD and ALERT_EMAIL_TO)


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


def send_low_stock_alert(alerts: pd.DataFrame) -> None:
    if alerts.empty:
        raise ValueError("No hay productos con stock bajo para notificar.")
    if not is_email_configured():
        raise ValueError(
            "Correo no configurado. Agrega SMTP_USER y SMTP_PASSWORD en el archivo .env"
        )

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
    message["Subject"] = subject
    message["From"] = SMTP_USER
    message["To"] = ALERT_EMAIL_TO
    message.attach(MIMEText(text_body, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [ALERT_EMAIL_TO], message.as_string())
