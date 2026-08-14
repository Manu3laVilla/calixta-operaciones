from __future__ import annotations

from datetime import date, datetime
from typing import Any

from services.alert_config_service import (
    get_active_alert_recipient_emails,
    get_alert_email_config,
    log_alert_send,
    resolve_due_slots,
)
from services.alert_service import get_low_stock_alerts
from services.email_service import is_email_configured, send_low_stock_alert


def _run_slot(
    *,
    slot: int,
    on_date: date,
    now: datetime,
    config: dict[str, Any],
    log: bool,
) -> dict[str, Any]:
    recipients = get_active_alert_recipient_emails()
    if not recipients:
        message = "No hay destinatarios activos configurados."
        if log:
            log_alert_send(
                slot=slot,
                on_date=on_date,
                destinatarios=[],
                productos_count=0,
                exito=False,
                mensaje=message,
            )
        return {"ok": False, "skipped": False, "slot": slot, "reason": message}

    if not is_email_configured():
        message = "SMTP no configurado en secrets/.env."
        if log:
            log_alert_send(
                slot=slot,
                on_date=on_date,
                destinatarios=recipients,
                productos_count=0,
                exito=False,
                mensaje=message,
            )
        return {"ok": False, "skipped": False, "slot": slot, "reason": message}

    alerts = get_low_stock_alerts()
    if bool(config.get("solo_si_hay_alertas", True)) and alerts.empty:
        message = "Sin productos en alerta; no se envió correo."
        if log:
            log_alert_send(
                slot=slot,
                on_date=on_date,
                destinatarios=recipients,
                productos_count=0,
                exito=True,
                mensaje=message,
            )
        return {"ok": True, "skipped": True, "slot": slot, "reason": message}

    try:
        send_low_stock_alert(alerts, recipients=recipients)
    except Exception as exc:
        message = str(exc)
        if log:
            log_alert_send(
                slot=slot,
                on_date=on_date,
                destinatarios=recipients,
                productos_count=len(alerts),
                exito=False,
                mensaje=message,
            )
        return {"ok": False, "skipped": False, "slot": slot, "reason": message}

    if log:
        try:
            log_alert_send(
                slot=slot,
                on_date=on_date,
                destinatarios=recipients,
                productos_count=len(alerts),
                exito=True,
                mensaje="Enviado correctamente.",
            )
        except Exception as exc:
            return {
                "ok": True,
                "skipped": False,
                "slot": slot,
                "recipients": recipients,
                "products": len(alerts),
                "sent_at": now.isoformat(),
                "log_error": str(exc),
            }

    return {
        "ok": True,
        "skipped": False,
        "slot": slot,
        "recipients": recipients,
        "products": len(alerts),
        "sent_at": now.isoformat(),
    }


def run_scheduled_alert_job(*, force: bool = False) -> dict[str, Any]:
    """Ejecuta envíos programados si corresponde por horario y configuración."""
    config = get_alert_email_config()
    if force:
        now = datetime.now()
        return _run_slot(
            slot=0,
            on_date=now.date(),
            now=now,
            config=config,
            log=False,
        )

    due_slots = resolve_due_slots()
    if not due_slots:
        return {
            "ok": True,
            "skipped": True,
            "reason": "Fuera de horario o envío automático inactivo.",
        }

    results = [
        _run_slot(slot=slot, on_date=on_date, now=now, config=config, log=True)
        for slot, on_date, now in due_slots
    ]
    sent = [item for item in results if item.get("ok") and not item.get("skipped")]
    failed = [item for item in results if not item.get("ok")]
    skipped = [item for item in results if item.get("skipped")]

    if sent:
        last = sent[-1]
        return {
            "ok": True,
            "skipped": False,
            "slots": [item["slot"] for item in sent],
            "slot": last["slot"],
            "recipients": last.get("recipients", []),
            "products": last.get("products", 0),
            "sent_at": last.get("sent_at"),
            "results": results,
        }
    if failed:
        first = failed[0]
        return {
            "ok": False,
            "skipped": False,
            "slot": first.get("slot"),
            "reason": first.get("reason", "Error desconocido."),
            "results": results,
        }

    first = skipped[0]
    return {
        "ok": True,
        "skipped": True,
        "slot": first.get("slot"),
        "reason": first.get("reason", "Nada que enviar."),
        "results": results,
    }
