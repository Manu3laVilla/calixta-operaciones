from __future__ import annotations

from typing import Any

import pandas as pd

from config import CATEGORIES, SIZES, TABLE_PRODUCTOS
from services.catalog_service import get_product_type, list_product_types
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
    if data.get("talla") is None:
        data["talla"] = ""
    return data


def _attach_type_names(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "tipo_id" not in df.columns:
        return df

    types = list_product_types()
    if types.empty:
        df = df.copy()
        df["tipo"] = ""
        return df

    merged = df.merge(
        types[["id", "nombre"]].rename(columns={"id": "tipo_id", "nombre": "tipo"}),
        on="tipo_id",
        how="left",
    )
    merged["tipo"] = merged["tipo"].fillna("")
    return merged


def _validate_tipo_categoria(tipo_id: str, categoria: str) -> None:
    tipo = get_product_type(tipo_id)
    if tipo is None:
        raise ValueError("Tipo de producto inválido.")
    if not _activo_to_bool(tipo.get("activo", True)):
        raise ValueError("El tipo de producto seleccionado está inactivo.")
    if str(tipo.get("categoria", "")) != str(categoria):
        raise ValueError("El tipo no corresponde a la categoría seleccionada.")


def _normalize_talla(categoria: str, talla: str | None) -> str | None:
    if categoria == "Accesorio":
        return None
    if not talla or talla not in SIZES:
        raise ValueError(f"Talla inválida. Opciones: {', '.join(SIZES)}")
    return talla


def list_products(active_only: bool = False) -> pd.DataFrame:
    df = get_db().get_dataframe(TABLE_PRODUCTOS)
    if df.empty:
        return df

    for col in ("precio", "stock", "stock_minimo"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if active_only and "activo" in df.columns:
        df = df[df["activo"].map(_activo_to_bool)]

    df = _attach_type_names(df)

    if "activo" in df.columns:
        df = df.copy()
        df["activo"] = df["activo"].map(_activo_to_ui)

    if "talla" in df.columns:
        df["talla"] = df["talla"].fillna("")

    return df


def get_product(product_id: str) -> dict[str, Any] | None:
    product = get_db().get_by_id(TABLE_PRODUCTOS, product_id)
    if product is None:
        return None
    normalized = _normalize_product_row(product)
    tipo = get_product_type(str(normalized.get("tipo_id", "")))
    normalized["tipo"] = tipo.get("nombre", "") if tipo else ""
    return normalized


def product_label(product: dict[str, Any]) -> str:
    ref = product.get("referencia", "")
    name = product.get("nombre", "")
    tipo = product.get("tipo", "")
    talla = product.get("talla", "")
    color = product.get("color", "")
    stock = product.get("stock", 0)
    precio = product.get("precio", 0)
    talla_part = f" | {talla}" if talla else ""
    tipo_part = f" | {tipo}" if tipo else ""
    return (
        f"{ref} | {name}{tipo_part}{talla_part} | {color} | "
        f"${precio:,.0f} COP (stock: {stock})"
    )


def create_product(
    referencia: str,
    nombre: str,
    color: str,
    talla: str | None,
    categoria: str,
    tipo_id: str,
    descripcion: str,
    stock: int,
    stock_minimo: int,
    precio: float,
) -> dict[str, Any]:
    if categoria not in CATEGORIES:
        raise ValueError(f"Categoría inválida. Opciones: {', '.join(CATEGORIES)}")
    _validate_tipo_categoria(tipo_id, categoria)
    talla_value = _normalize_talla(categoria, talla)

    product = {
        "id": new_id("PRD"),
        "referencia": referencia.strip(),
        "nombre": nombre.strip(),
        "color": color.strip(),
        "talla": talla_value,
        "categoria": categoria,
        "tipo_id": tipo_id,
        "descripcion": descripcion.strip(),
        "stock": int(stock),
        "stock_minimo": int(stock_minimo),
        "precio": float(precio),
        "activo": True,
        "fecha_registro": now_iso(),
    }
    created = get_db().insert(TABLE_PRODUCTOS, product)
    return get_product(str(created["id"])) or _normalize_product_row(created)


def update_product(product_id: str, updates: dict[str, Any]) -> bool:
    product = get_db().get_by_id(TABLE_PRODUCTOS, product_id)
    if product is None:
        return False

    payload = dict(updates)
    categoria = str(payload.get("categoria", product.get("categoria", "")))

    if "tipo_id" in payload or "categoria" in payload:
        tipo_id = str(payload.get("tipo_id", product.get("tipo_id", "")))
        _validate_tipo_categoria(tipo_id, categoria)
        payload["tipo_id"] = tipo_id

    if "categoria" in payload and payload["categoria"] not in CATEGORIES:
        raise ValueError(f"Categoría inválida. Opciones: {', '.join(CATEGORIES)}")

    if "talla" in payload or "categoria" in payload:
        talla_input = payload.get("talla", product.get("talla"))
        payload["talla"] = _normalize_talla(categoria, talla_input or None)

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
