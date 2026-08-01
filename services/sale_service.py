from __future__ import annotations

from typing import Any

import pandas as pd

from config import SHEET_VENTAS
from services.sheets_db import get_db, new_id


def list_sales(
    cliente_id: str | None = None,
    pedido_id: str | None = None,
    producto_id: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
) -> pd.DataFrame:
    df = get_db().get_dataframe(SHEET_VENTAS)
    if df.empty:
        return df

    for col in ("cantidad", "precio_unitario", "subtotal"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if cliente_id:
        df = df[df["cliente_id"].astype(str) == str(cliente_id)]
    if pedido_id:
        df = df[df["pedido_id"].astype(str) == str(pedido_id)]
    if producto_id:
        df = df[df["producto_id"].astype(str) == str(producto_id)]
    if fecha_desde and "fecha_entrega" in df.columns:
        df = df[df["fecha_entrega"].astype(str) >= fecha_desde]
    if fecha_hasta and "fecha_entrega" in df.columns:
        df = df[df["fecha_entrega"].astype(str) <= fecha_hasta]

    if "fecha_entrega" in df.columns:
        return df.sort_values("fecha_entrega", ascending=False)
    return df


def create_sale_from_order(
    pedido_id: str,
    cliente_id: str,
    cliente_nombre: str,
    producto: dict[str, Any],
    cantidad: int,
    precio_unitario: float,
    fecha_entrega: str,
) -> dict[str, Any]:
    qty = int(cantidad)
    subtotal = float(precio_unitario) * qty

    sale = {
        "id": new_id("VTA"),
        "fecha_entrega": fecha_entrega,
        "pedido_id": pedido_id,
        "cliente_id": cliente_id,
        "cliente_nombre": cliente_nombre,
        "producto_id": producto["id"],
        "referencia": producto.get("referencia", ""),
        "producto_nombre": producto.get("nombre", ""),
        "color": producto.get("color", ""),
        "talla": producto.get("talla", ""),
        "cantidad": qty,
        "precio_unitario": float(precio_unitario),
        "subtotal": subtotal,
    }
    get_db().append_row(SHEET_VENTAS, list(sale.values()))
    return sale
