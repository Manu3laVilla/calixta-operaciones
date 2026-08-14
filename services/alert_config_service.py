from __future__ import annotations

import re
from datetime import date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from app_config import (
    TABLE_ALERTAS_DESTINATARIOS,
    TABLE_ALERTAS_ENVIOS_LOG,
    TABLE_CONFIG_ALERTAS_EMAIL,
)
from services.supabase_db import get_db, new_id, now_iso

CONFIG_ID = "DEFAULT"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

DEFAULT_CONFIG: dict[str, Any] = {
    "id": CONFIG_ID,
    "activo": False,
    "envios_por_dia": 1,
    "horario_1": "08:00:00",
    "horario_2": "14:00:00",
    "horario_3": "18:00:00",
    "solo_si_hay_alertas": True,
    "zona_horaria": "America/Bogota",
}


def _activo_to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("si", "sí", "true", "1", "yes")


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if not EMAIL_PATTERN.match(normalized):
        raise ValueError(f"Correo inválido: {email}")
    return normalized


def _parse_time_value(value: Any) -> time:
    if isinstance(value, time):
        return value
    text = str(value or "08:00").strip()
    if len(text) == 5:
        text = f"{text}:00"
    hour, minute, second = (int(part) for part in text.split(":"))
    return time(hour=hour, minute=minute, second=second)


def _time_to_input(value: Any) -> str:
    parsed = _parse_time_value(value)
    return parsed.strftime("%H:%M")


def get_alert_email_config() -> dict[str, Any]:
    row = get_db().get_by_id(TABLE_CONFIG_ALERTAS_EMAIL, CONFIG_ID)
    if row is None:
        return dict(DEFAULT_CONFIG)
    merged = dict(DEFAULT_CONFIG)
    merged.update(row)
    return merged


def save_alert_email_config(
    *,
    activo: bool,
    envios_por_dia: int,
    horario_1: str,
    horario_2: str,
    horario_3: str,
    solo_si_hay_alertas: bool,
    zona_horaria: str = "America/Bogota",
) -> dict[str, Any]:
    envios = int(envios_por_dia)
    if envios not in (1, 2, 3):
        raise ValueError("Los envíos por día deben ser 1, 2 o 3.")

    payload = {
        "activo": bool(activo),
        "envios_por_dia": envios,
        "horario_1": _parse_time_value(horario_1).isoformat(),
        "horario_2": _parse_time_value(horario_2).isoformat(),
        "horario_3": _parse_time_value(horario_3).isoformat(),
        "solo_si_hay_alertas": bool(solo_si_hay_alertas),
        "zona_horaria": zona_horaria.strip() or "America/Bogota",
        "fecha_actualizacion": now_iso(),
    }

    db = get_db()
    if db.get_by_id(TABLE_CONFIG_ALERTAS_EMAIL, CONFIG_ID) is None:
        created = db.insert(TABLE_CONFIG_ALERTAS_EMAIL, {"id": CONFIG_ID, **payload})
        return created
    db.update_by_id(TABLE_CONFIG_ALERTAS_EMAIL, CONFIG_ID, payload)
    return get_alert_email_config()


def list_alert_recipients(*, active_only: bool = False) -> pd.DataFrame:
    df = get_db().get_dataframe(TABLE_ALERTAS_DESTINATARIOS)
    if df.empty:
        return df
    if active_only and "activo" in df.columns:
        df = df[df["activo"].map(_activo_to_bool)]
    if "email" in df.columns:
        return df.sort_values("email", ascending=True)
    return df


def get_active_alert_recipient_emails() -> list[str]:
    df = list_alert_recipients(active_only=True)
    if df.empty or "email" not in df.columns:
        return []
    return [str(email) for email in df["email"].tolist()]


def create_alert_recipient(email: str, nombre: str = "") -> dict[str, Any]:
    normalized = _normalize_email(email)
    existing = get_db().get_dataframe(TABLE_ALERTAS_DESTINATARIOS)
    if not existing.empty and "email" in existing.columns:
        matches = existing["email"].astype(str).str.lower() == normalized
        if matches.any():
            raise ValueError(f"Ya existe el destinatario {normalized}.")

    record = {
        "id": new_id("ALT"),
        "email": normalized,
        "nombre": nombre.strip(),
        "activo": True,
        "fecha_registro": now_iso(),
    }
    return get_db().insert(TABLE_ALERTAS_DESTINATARIOS, record)


def update_alert_recipient(recipient_id: str, updates: dict[str, Any]) -> bool:
    payload = dict(updates)
    if "email" in payload:
        payload["email"] = _normalize_email(str(payload["email"]))
    if "nombre" in payload:
        payload["nombre"] = str(payload["nombre"]).strip()
    if "activo" in payload:
        payload["activo"] = _activo_to_bool(payload["activo"])
    return get_db().update_by_id(TABLE_ALERTAS_DESTINATARIOS, recipient_id, payload)


def delete_alert_recipient(recipient_id: str) -> bool:
    get_db().delete_by_id(TABLE_ALERTAS_DESTINATARIOS, recipient_id)
    return True


def list_alert_send_logs(limit: int = 20) -> pd.DataFrame:
    df = get_db().get_dataframe(TABLE_ALERTAS_ENVIOS_LOG)
    if df.empty:
        return df
    if "enviado_en" in df.columns:
        return df.sort_values("enviado_en", ascending=False).head(limit)
    return df.head(limit)


def was_slot_sent_today(
    slot: int,
    *,
    on_date: date | None = None,
    window_minutes: int = 25,
) -> bool:
    """True si ese slot ya se procesó hoy cerca de su horario programado."""
    config = get_alert_email_config()
    tz_name = str(config.get("zona_horaria") or "America/Bogota")
    tz = ZoneInfo(tz_name)
    target_date = on_date or datetime.now(tz).date()
    target_iso = target_date.isoformat()

    scheduled_time: time | None = None
    for slot_number, scheduled in configured_schedule_times(config):
        if slot_number == int(slot):
            scheduled_time = scheduled
            break
    if scheduled_time is None:
        return False

    scheduled_dt = datetime.combine(target_date, scheduled_time, tzinfo=tz)
    df = get_db().get_dataframe(TABLE_ALERTAS_ENVIOS_LOG)
    if df.empty:
        return False

    for _, row in df.iterrows():
        if int(row.get("slot", 0)) != int(slot):
            continue
        if not _activo_to_bool(row.get("exito", False)):
            continue
        row_date = str(row.get("fecha", ""))[:10]
        if row_date != target_iso:
            continue

        sent_at = pd.to_datetime(row.get("enviado_en"), errors="coerce", utc=True)
        if pd.isna(sent_at):
            continue
        sent_local = sent_at.tz_convert(tz)
        delta_minutes = abs((sent_local - scheduled_dt).total_seconds()) / 60
        if delta_minutes <= window_minutes:
            return True
    return False


def log_alert_send(
    *,
    slot: int,
    on_date: date,
    destinatarios: list[str],
    productos_count: int,
    exito: bool,
    mensaje: str = "",
) -> None:
    payload = {
        "enviado_en": now_iso(),
        "destinatarios": ", ".join(destinatarios),
        "productos_count": int(productos_count),
        "exito": bool(exito),
        "mensaje": mensaje[:500],
    }
    db = get_db()
    updated = (
        db.client.table(TABLE_ALERTAS_ENVIOS_LOG)
        .update(payload)
        .eq("fecha", on_date.isoformat())
        .eq("slot", int(slot))
        .execute()
    )
    if updated.data:
        return

    db.insert(
        TABLE_ALERTAS_ENVIOS_LOG,
        {
            "slot": int(slot),
            "fecha": on_date.isoformat(),
            **payload,
        },
    )


def configured_schedule_times(config: dict[str, Any] | None = None) -> list[tuple[int, time]]:
    cfg = config or get_alert_email_config()
    count = int(cfg.get("envios_por_dia") or 1)
    slots: list[tuple[int, time]] = []
    for slot in range(1, min(count, 3) + 1):
        slots.append((slot, _parse_time_value(cfg.get(f"horario_{slot}"))))
    return slots


def resolve_due_slots(*, window_minutes: int = 25) -> list[tuple[int, date, datetime]]:
    config = get_alert_email_config()
    if not _activo_to_bool(config.get("activo", False)):
        return []

    tz_name = str(config.get("zona_horaria") or "America/Bogota")
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    today = now.date()
    due: list[tuple[int, date, datetime]] = []

    for slot, scheduled in configured_schedule_times(config):
        scheduled_dt = datetime.combine(today, scheduled, tzinfo=tz)
        delta_minutes = abs((now - scheduled_dt).total_seconds()) / 60
        if delta_minutes <= window_minutes and not was_slot_sent_today(
            slot,
            on_date=today,
            window_minutes=window_minutes,
        ):
            due.append((slot, today, now))
    return due


def resolve_due_slot(*, window_minutes: int = 25) -> tuple[int, date, datetime] | None:
    slots = resolve_due_slots(window_minutes=window_minutes)
    return slots[0] if slots else None


def format_config_summary(config: dict[str, Any] | None = None) -> str:
    cfg = config or get_alert_email_config()
    times = ", ".join(
        _time_to_input(scheduled)
        for _, scheduled in configured_schedule_times(cfg)
    )
    estado = "activo" if _activo_to_bool(cfg.get("activo")) else "inactivo"
    return f"Envío automático {estado}: {cfg.get('envios_por_dia', 1)} vez/veces al día ({times})."


def time_input_defaults(config: dict[str, Any] | None = None) -> tuple[str, str, str]:
    cfg = config or get_alert_email_config()
    return (
        _time_to_input(cfg.get("horario_1")),
        _time_to_input(cfg.get("horario_2")),
        _time_to_input(cfg.get("horario_3")),
    )
