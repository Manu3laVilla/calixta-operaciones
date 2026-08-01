from __future__ import annotations

import json
from typing import Any

import pandas as pd

from config import DELIVERED_STATE, ORDER_STATES, SHEET_PEDIDOS
from services.product_service import adjust_stock, get_product
from services.sale_service import create_sale_from_order
from services.sheets_db import get_db, new_id, now_str


def list_orders(estado: str | None = None) -> pd.DataFrame:
    df = get_db().get_dataframe(SHEET_PEDIDOS)
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
    df = list_orders()
    if df.empty:
        return None
    match = df[df["id"].astype(str) == str(order_id)]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def _parse_items(items_json: str) -> list[dict[str, Any]]:
    if not items_json:
        return []
    try:
        items = json.loads(items_json)
        return items if isinstance(items, list) else []
    except json.JSONDecodeError:
        return []


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


def create_order(
    cliente_id: str,
    cliente_nombre: str,
    items: list[dict[str, Any]],
    direccion_entrega: str,
    notas: str = "",
) -> dict[str, Any]:
    normalized_items, total = _normalize_items(items)

    order = {
        "id": new_id("PED"),
        "cliente_id": cliente_id,
        "cliente_nombre": cliente_nombre,
        "items_json": json.dumps(normalized_items, ensure_ascii=False),
        "total": total,
        "estado": "Recibido",
        "direccion_entrega": direccion_entrega.strip(),
        "fecha_entrega": "",
        "fecha_creacion": now_str(),
        "fecha_actualizacion": now_str(),
        "notas": notas.strip(),
    }
    get_db().append_row(SHEET_PEDIDOS, list(order.values()))
    return order


def update_order(
    order_id: str,
    cliente_id: str,
    cliente_nombre: str,
    items: list[dict[str, Any]],
    direccion_entrega: str,
    notas: str = "",
) -> bool:
    db = get_db()
    row_number = db.find_row_number(SHEET_PEDIDOS, "id", order_id)
    if row_number is None:
        return False

    order = get_order(order_id)
    if order is None:
        return False

    _ensure_editable(order)
    normalized_items, total = _normalize_items(items)

    order.update(
        {
            "cliente_id": cliente_id,
            "cliente_nombre": cliente_nombre,
            "items_json": json.dumps(normalized_items, ensure_ascii=False),
            "total": total,
            "direccion_entrega": direccion_entrega.strip(),
            "notas": notas.strip(),
            "fecha_actualizacion": now_str(),
        }
    )
    db.update_row(SHEET_PEDIDOS, row_number, list(order.values()))
    return True


def delete_order(order_id: str) -> bool:
    db = get_db()
    order = get_order(order_id)
    if order is None:
        return False

    _ensure_editable(order)
    row_number = db.find_row_number(SHEET_PEDIDOS, "id", order_id)
    if row_number is None:
        return False

    db.delete_row(SHEET_PEDIDOS, row_number)
    return True


def _deliver_order(order: dict[str, Any], fecha_entrega: str) -> None:
    items = _parse_items(str(order.get("items_json", "")))
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

    db = get_db()
    row_number = db.find_row_number(SHEET_PEDIDOS, "id", order_id)
    if row_number is None:
        return False

    order = get_order(order_id)
    if order is None:
        return False

    previous_status = str(order.get("estado", ""))
    if previous_status == DELIVERED_STATE:
        raise ValueError("Un pedido entregado no puede cambiar de estado.")

    if new_status == DELIVERED_STATE:
        if not fecha_entrega:
            raise ValueError("Debe indicar la fecha y hora de entrega.")
        _deliver_order(order, fecha_entrega)
        order["fecha_entrega"] = fecha_entrega

    order["estado"] = new_status
    order["fecha_actualizacion"] = now_str()
    db.update_row(SHEET_PEDIDOS, row_number, list(order.values()))
    return True


def get_order_items(order_id: str) -> list[dict[str, Any]]:
    order = get_order(order_id)
    if order is None:
        return []
    return _parse_items(str(order.get("items_json", "")))
