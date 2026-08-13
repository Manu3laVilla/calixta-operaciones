from __future__ import annotations

from typing import Any

import pandas as pd

from config import TABLE_CLIENTES
from services.supabase_db import get_db, new_id, now_iso


def list_customers() -> pd.DataFrame:
    return get_db().get_dataframe(TABLE_CLIENTES)


def get_customer(customer_id: str) -> dict[str, Any] | None:
    return get_db().get_by_id(TABLE_CLIENTES, customer_id)


def create_customer(
    nombre: str,
    email: str,
    telefono: str,
    direccion: str,
    notas: str = "",
) -> dict[str, Any]:
    customer = {
        "id": new_id("CLI"),
        "nombre": nombre.strip(),
        "email": email.strip(),
        "telefono": telefono.strip(),
        "direccion": direccion.strip(),
        "notas": notas.strip(),
        "fecha_registro": now_iso(),
    }
    return get_db().insert(TABLE_CLIENTES, customer)


def update_customer(customer_id: str, updates: dict[str, Any]) -> bool:
    if get_customer(customer_id) is None:
        return False
    return get_db().update_by_id(TABLE_CLIENTES, customer_id, updates)
