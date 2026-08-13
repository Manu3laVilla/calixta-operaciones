from __future__ import annotations

from typing import Any

import pandas as pd

from config import CATEGORIES, SIZES, TABLE_PRODUCTOS
from services.supabase_db import get_db, new_id, now_iso


def _activo_to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("si", "sí", "true", "1", "yes")


def _activo_to_ui(value: Any) -> str:
    return "Si" if _activo_to_bool(value) else "No"


def _normalize_product_row(row: dict[str, Any]) -> dict[str, Any]:
    data = dict(row)
    if "activo" in data:
        data["activo"] = _activo_to_ui(data["activo"])
    return data


def list_products(active_only: bool = False) -> pd.DataFrame:
    df = get_db().get_dataframe(TABLE_PRODUCTOS)
    if df.empty:
        return df

    for col in ("precio", "stock", "stock_minimo"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if active_only and "activo" in df.columns:
        df = df[df["activo"].map(_activo_to_bool)]

    if "activo" in df.columns:
        df = df.copy()
        df["activo"] = df["activo"].map(_activo_to_ui)

    return df


def get_product(product_id: str) -> dict[str, Any] | None:
    product = get_db().get_by_id(TABLE_PRODUCTOS, product_id)
    if product is None:
        return None
    return _normalize_product_row(product)


def product_label(product: dict[str, Any]) -> str:
    ref = product.get("referencia", "")
    name = product.get("nombre", "")
    talla = product.get("talla", "")
    color = product.get("color", "")
    stock = product.get("stock", 0)
    precio = product.get("precio", 0)
    return f"{ref} | {name} | {talla} | {color} | ${precio:,.0f} COP (stock: {stock})"


def create_product(
    referencia: str,
    nombre: str,
    color: str,
    talla: str,
    categoria: str,
    descripcion: str,
    stock: int,
    stock_minimo: int,
    precio: float,
) -> dict[str, Any]:
    if talla not in SIZES:
        raise ValueError(f"Talla inválida. Opciones: {', '.join(SIZES)}")
    if categoria not in CATEGORIES:
        raise ValueError(f"Categoría inválida. Opciones: {', '.join(CATEGORIES)}")

    product = {
        "id": new_id("PRD"),
        "referencia": referencia.strip(),
        "nombre": nombre.strip(),
        "color": color.strip(),
        "talla": talla,
        "categoria": categoria,
        "descripcion": descripcion.strip(),
        "stock": int(stock),
        "stock_minimo": int(stock_minimo),
        "precio": float(precio),
        "activo": True,
        "fecha_registro": now_iso(),
    }
    created = get_db().insert(TABLE_PRODUCTOS, product)
    return _normalize_product_row(created)


def update_product(product_id: str, updates: dict[str, Any]) -> bool:
    product = get_db().get_by_id(TABLE_PRODUCTOS, product_id)
    if product is None:
        return False

    payload = dict(updates)
    if "talla" in payload and payload["talla"] not in SIZES:
        raise ValueError(f"Talla inválida. Opciones: {', '.join(SIZES)}")
    if "categoria" in payload and payload["categoria"] not in CATEGORIES:
        raise ValueError(f"Categoría inválida. Opciones: {', '.join(CATEGORIES)}")
    if "activo" in payload:
        payload["activo"] = _activo_to_bool(payload["activo"])

    for key in ("stock", "stock_minimo"):
        if key in payload:
            payload[key] = int(payload[key])
    if "precio" in payload:
        payload["precio"] = float(payload["precio"])

    return get_db().update_by_id(TABLE_PRODUCTOS, product_id, payload)


def adjust_stock(product_id: str, delta: int) -> bool:
    product = get_product(product_id)
    if product is None:
        return False

    new_stock = int(product.get("stock", 0)) + int(delta)
    if new_stock < 0:
        raise ValueError("Stock insuficiente para esta operación.")

    return update_product(product_id, {"stock": new_stock})
