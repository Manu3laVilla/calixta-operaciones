from __future__ import annotations

from typing import Any

import pandas as pd

from config import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    MOVEMENT_TYPE_EXPENSE,
    MOVEMENT_TYPE_INCOME,
    SHEET_CONTABILIDAD,
)
from services.sheets_db import get_db, new_id, now_str


def list_movements() -> pd.DataFrame:
    df = get_db().get_dataframe(SHEET_CONTABILIDAD)
    if df.empty:
        return df
    df = df.copy()
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0.0)
    if "fecha" in df.columns:
        df = df.sort_values("fecha", ascending=False)
    return df


def get_movement(movement_id: str) -> dict[str, Any] | None:
    df = list_movements()
    if df.empty:
        return None
    match = df[df["id"].astype(str) == str(movement_id)]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def _normalize_fecha(fecha: str) -> str:
    value = str(fecha).strip()
    if " " in value:
        return value.split(" ")[0]
    return value


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

    valid_categories = INCOME_CATEGORIES if tipo == MOVEMENT_TYPE_INCOME else EXPENSE_CATEGORIES
    if categoria not in valid_categories:
        raise ValueError("Categoría inválida para el tipo de movimiento.")

    timestamp = now_str()
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
    get_db().append_row(SHEET_CONTABILIDAD, list(movement.values()))
    return movement


def update_movement(movement_id: str, updates: dict[str, Any]) -> bool:
    db = get_db()
    row_number = db.find_row_number(SHEET_CONTABILIDAD, "id", movement_id)
    if row_number is None:
        return False

    movement = get_movement(movement_id)
    if movement is None:
        return False

    if "tipo" in updates:
        tipo = str(updates["tipo"])
        categoria = str(updates.get("categoria", movement.get("categoria", "")))
        valid = INCOME_CATEGORIES if tipo == MOVEMENT_TYPE_INCOME else EXPENSE_CATEGORIES
        if categoria not in valid:
            raise ValueError("Categoría inválida para el tipo de movimiento.")

    if "monto" in updates and float(updates["monto"]) <= 0:
        raise ValueError("El monto debe ser mayor a cero.")

    if "fecha" in updates:
        updates["fecha"] = _normalize_fecha(str(updates["fecha"]))

    movement.update(updates)
    movement["fecha_actualizacion"] = now_str()
    db.update_row(SHEET_CONTABILIDAD, row_number, list(movement.values()))
    return True


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
