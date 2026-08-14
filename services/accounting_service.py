from __future__ import annotations

from typing import Any

import pandas as pd

from config import (
    MOVEMENT_TYPE_EXPENSE,
    MOVEMENT_TYPE_INCOME,
    TABLE_CONTABILIDAD,
)
from services.catalog_service import expense_type_names, income_type_names
from services.supabase_db import get_db, new_id, now_iso


def list_movements() -> pd.DataFrame:
    df = get_db().get_dataframe(TABLE_CONTABILIDAD)
    if df.empty:
        return df
    df = df.copy()
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0.0)
    if "fecha" in df.columns:
        df = df.sort_values("fecha", ascending=False)
    return df


def get_movement(movement_id: str) -> dict[str, Any] | None:
    return get_db().get_by_id(TABLE_CONTABILIDAD, movement_id)


def _normalize_fecha(fecha: str) -> str:
    value = str(fecha).strip()
    if " " in value:
        return value.split(" ")[0]
    return value


def _valid_income_categories() -> list[str]:
    names = income_type_names(active_only=False)
    return names if names else ["Capital", "Inversión", "Otros ingresos"]


def _valid_expense_categories() -> list[str]:
    names = expense_type_names(active_only=False)
    return names if names else ["Insumos", "Equipos", "Otros gastos"]


def create_movement(
    tipo: str,
    categoria: str,
    concepto: str,
    monto: float,
    fecha: str,
    notas: str = "",
) -> dict[str, Any]:
    if tipo not in (MOVEMENT_TYPE_INCOME, MOVEMENT_TYPE_EXPENSE):
        raise ValueError("Tipo de movimiento inválido.")
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a cero.")

    valid_categories = (
        _valid_income_categories()
        if tipo == MOVEMENT_TYPE_INCOME
        else _valid_expense_categories()
    )
    if categoria not in valid_categories:
        raise ValueError("Categoría inválida para el tipo de movimiento.")

    timestamp = now_iso()
    movement = {
        "id": new_id("FIN"),
        "fecha": _normalize_fecha(fecha),
        "tipo": tipo,
        "categoria": categoria,
        "concepto": concepto.strip(),
        "monto": float(monto),
        "notas": notas.strip(),
        "fecha_registro": timestamp,
        "fecha_actualizacion": timestamp,
    }
    return get_db().insert(TABLE_CONTABILIDAD, movement)


def update_movement(movement_id: str, updates: dict[str, Any]) -> bool:
    movement = get_movement(movement_id)
    if movement is None:
        return False

    payload = dict(updates)

    if "tipo" in payload:
        tipo = str(payload["tipo"])
        categoria = str(payload.get("categoria", movement.get("categoria", "")))
        valid = (
            _valid_income_categories()
            if tipo == MOVEMENT_TYPE_INCOME
            else _valid_expense_categories()
        )
        if categoria not in valid:
            raise ValueError("Categoría inválida para el tipo de movimiento.")

    if "monto" in payload and float(payload["monto"]) <= 0:
        raise ValueError("El monto debe ser mayor a cero.")

    if "fecha" in payload:
        payload["fecha"] = _normalize_fecha(str(payload["fecha"]))

    payload["fecha_actualizacion"] = now_iso()
    return get_db().update_by_id(TABLE_CONTABILIDAD, movement_id, payload)


def filter_movements(
    movements: pd.DataFrame,
    *,
    tipo: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
) -> pd.DataFrame:
    if movements.empty:
        return movements

    df = movements.copy()
    if tipo and tipo != "Todos":
        df = df[df["tipo"].astype(str) == str(tipo)]
    if fecha_desde:
        df = df[df["fecha"].astype(str) >= str(fecha_desde)]
    if fecha_hasta:
        df = df[df["fecha"].astype(str) <= str(fecha_hasta)]
    return df.sort_values("fecha", ascending=False) if "fecha" in df.columns else df


def summary_totals(movements: pd.DataFrame) -> tuple[float, float, float]:
    if movements.empty:
        return 0.0, 0.0, 0.0

    ingresos = float(
        movements[movements["tipo"] == MOVEMENT_TYPE_INCOME]["monto"].sum()
    )
    gastos = float(
        movements[movements["tipo"] == MOVEMENT_TYPE_EXPENSE]["monto"].sum()
    )
    return ingresos, gastos, ingresos - gastos


def summary_by_category(movements: pd.DataFrame) -> pd.DataFrame:
    if movements.empty:
        return pd.DataFrame(columns=["tipo", "categoria", "monto"])

    grouped = (
        movements.groupby(["tipo", "categoria"], as_index=False)["monto"]
        .sum()
        .sort_values(["tipo", "monto"], ascending=[True, False])
    )
    grouped.columns = ["tipo", "categoria", "monto"]
    return grouped


def movement_label(row: dict[str, Any]) -> str:
    monto = float(row.get("monto", 0) or 0)
    return (
        f"{row.get('fecha', '')} | {row.get('tipo', '')} | "
        f"{row.get('concepto', '')} (${monto:,.0f}) — {row.get('id', '')}"
    )
