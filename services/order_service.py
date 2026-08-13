from __future__ import annotations

from typing import Any

import pandas as pd

from config import DELIVERED_STATE, ORDER_STATES, TABLE_PEDIDO_ITEMS, TABLE_PEDIDOS
from services.product_service import adjust_stock, get_product
from services.sale_service import create_sale_from_order
from services.supabase_db import get_db, new_id, now_iso


def _items_to_records(
    pedido_id: str,
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "pedido_id": pedido_id,
            "producto_id": item["producto_id"],
            "referencia": item.get("referencia", ""),
            "producto_nombre": item.get("producto_nombre", ""),
            "color": item.get("color", ""),
            "talla": item.get("talla", ""),
            "cantidad": int(item["cantidad"]),
            "precio_unitario": float(item["precio_unitario"]),
            "subtotal": float(item["subtotal"]),
        }
        for item in items
    ]


def _normalize_items(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], float]:
    if not items:
        raise ValueError("El pedido debe incluir al menos un producto.")

    normalized: list[dict[str, Any]] = []
    total = 0.0

    for item in items:
        product = get_product(str(item["producto_id"]))
        if product is None:
            raise ValueError(f"Producto no encontrado: {item['producto_id']}")

        qty = int(item["cantidad"])
        if qty <= 0:
            raise ValueError("Cada producto debe tener cantidad mayor a cero.")

        price = float(product.get("precio", 0))
        subtotal = price * qty
        total += subtotal

        normalized.append(
            {
                "producto_id": product["id"],
                "referencia": product.get("referencia", ""),
                "producto_nombre": product.get("nombre", ""),
                "color": product.get("color", ""),
                "talla": product.get("talla", ""),
                "cantidad": qty,
                "precio_unitario": price,
                "subtotal": subtotal,
            }
        )

    return normalized, total


def _ensure_editable(order: dict[str, Any]) -> None:
    if str(order.get("estado", "")) == DELIVERED_STATE:
        raise ValueError("No se puede modificar un pedido ya entregado.")


def list_orders(estado: str | None = None) -> pd.DataFrame:
    df = get_db().get_dataframe(TABLE_PEDIDOS)
    if df.empty:
        return df

    if "total" in df.columns:
        df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0)

    if estado:
        df = df[df["estado"].astype(str) == estado]

    if "fecha_creacion" in df.columns:
        return df.sort_values("fecha_creacion", ascending=False)
    return df


def get_order(order_id: str) -> dict[str, Any] | None:
    return get_db().get_by_id(TABLE_PEDIDOS, order_id)


def create_order(
    cliente_id: str,
    cliente_nombre: str,
    items: list[dict[str, Any]],
    direccion_entrega: str,
    notas: str = "",
) -> dict[str, Any]:
    normalized_items, total = _normalize_items(items)
    db = get_db()
    timestamp = now_iso()

    order = {
        "id": new_id("PED"),
        "cliente_id": cliente_id,
        "cliente_nombre": cliente_nombre,
        "total": total,
        "estado": "Recibido",
        "direccion_entrega": direccion_entrega.strip(),
        "fecha_entrega": None,
        "fecha_creacion": timestamp,
        "fecha_actualizacion": timestamp,
        "notas": notas.strip(),
    }
    created = db.insert(TABLE_PEDIDOS, order)
    db.insert_many(TABLE_PEDIDO_ITEMS, _items_to_records(created["id"], normalized_items))
    return created


def update_order(
    order_id: str,
    cliente_id: str,
    cliente_nombre: str,
    items: list[dict[str, Any]],
    direccion_entrega: str,
    notas: str = "",
) -> bool:
    order = get_order(order_id)
    if order is None:
        return False

    _ensure_editable(order)
    normalized_items, total = _normalize_items(items)
    db = get_db()

    updated = db.update_by_id(
        TABLE_PEDIDOS,
        order_id,
        {
            "cliente_id": cliente_id,
            "cliente_nombre": cliente_nombre,
            "total": total,
            "direccion_entrega": direccion_entrega.strip(),
            "notas": notas.strip(),
            "fecha_actualizacion": now_iso(),
        },
    )
    if not updated:
        return False

    db.delete_where(TABLE_PEDIDO_ITEMS, column="pedido_id", value=order_id)
    db.insert_many(TABLE_PEDIDO_ITEMS, _items_to_records(order_id, normalized_items))
    return True


def delete_order(order_id: str) -> bool:
    order = get_order(order_id)
    if order is None:
        return False

    _ensure_editable(order)
    get_db().delete_by_id(TABLE_PEDIDOS, order_id)
    return True


def _deliver_order(order: dict[str, Any], fecha_entrega: str) -> None:
    items = get_order_items(str(order["id"]))
    for item in items:
        product = get_product(str(item["producto_id"]))
        if product is None:
            raise ValueError(f"Producto no encontrado: {item['producto_id']}")

        adjust_stock(str(item["producto_id"]), -int(item["cantidad"]))
        create_sale_from_order(
            pedido_id=str(order["id"]),
            cliente_id=str(order["cliente_id"]),
            cliente_nombre=str(order["cliente_nombre"]),
            producto=product,
            cantidad=int(item["cantidad"]),
            precio_unitario=float(item["precio_unitario"]),
            fecha_entrega=fecha_entrega,
        )


def update_order_status(
    order_id: str,
    new_status: str,
    fecha_entrega: str | None = None,
) -> bool:
    if new_status not in ORDER_STATES:
        raise ValueError(f"Estado inválido. Usa uno de: {', '.join(ORDER_STATES)}")

    order = get_order(order_id)
    if order is None:
        return False

    previous_status = str(order.get("estado", ""))
    if previous_status == DELIVERED_STATE:
        raise ValueError("Un pedido entregado no puede cambiar de estado.")

    updates: dict[str, Any] = {
        "estado": new_status,
        "fecha_actualizacion": now_iso(),
    }

    if new_status == DELIVERED_STATE:
        if not fecha_entrega:
            raise ValueError("Debe indicar la fecha y hora de entrega.")
        _deliver_order(order, fecha_entrega)
        updates["fecha_entrega"] = fecha_entrega

    return get_db().update_by_id(TABLE_PEDIDOS, order_id, updates)


def get_order_items(order_id: str) -> list[dict[str, Any]]:
    rows = get_db().select_where(
        TABLE_PEDIDO_ITEMS,
        column="pedido_id",
        value=order_id,
    )
    return [
        {
            "producto_id": row["producto_id"],
            "referencia": row.get("referencia", ""),
            "producto_nombre": row.get("producto_nombre", ""),
            "color": row.get("color", ""),
            "talla": row.get("talla", ""),
            "cantidad": row["cantidad"],
            "precio_unitario": row["precio_unitario"],
            "subtotal": row["subtotal"],
        }
        for row in rows
    ]
