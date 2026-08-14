from __future__ import annotations

from typing import Any

import pandas as pd

from config import TABLE_PEDIDO_ITEMS, TABLE_PEDIDOS
from services.product_service import adjust_stock, get_product
from services.sale_service import create_sale_from_order, delete_sales_by_pedido
from services.catalog_service import (
    get_initial_order_state_name,
    get_order_state_by_name,
    get_allowed_next_states,
    order_state_blocks_editing,
    order_state_names,
)
from services.supabase_db import get_db, new_id, now_iso


def _activo_to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("si", "sí", "true", "1", "yes")


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
            "talla": item.get("talla") or "",
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
                "talla": product.get("talla", "") or "",
                "cantidad": qty,
                "precio_unitario": price,
                "subtotal": subtotal,
            }
        )

    return normalized, total


def _ensure_editable(order: dict[str, Any]) -> None:
    if order_state_blocks_editing(str(order.get("estado", ""))):
        raise ValueError("No se puede modificar un pedido en su estado actual.")


def _reserve_stock(items: list[dict[str, Any]]) -> None:
    for item in items:
        adjust_stock(str(item["producto_id"]), -int(item["cantidad"]))


def _release_stock(items: list[dict[str, Any]]) -> None:
    for item in items:
        adjust_stock(str(item["producto_id"]), int(item["cantidad"]))


def _register_sale(order: dict[str, Any], items: list[dict[str, Any]], fecha_entrega: str) -> None:
    for item in items:
        product = get_product(str(item["producto_id"]))
        if product is None:
            raise ValueError(f"Producto no encontrado: {item['producto_id']}")

        create_sale_from_order(
            pedido_id=str(order["id"]),
            cliente_id=str(order["cliente_id"]),
            cliente_nombre=str(order["cliente_nombre"]),
            producto=product,
            cantidad=int(item["cantidad"]),
            precio_unitario=float(item["precio_unitario"]),
            fecha_entrega=fecha_entrega,
        )


def _apply_genera_venta(order: dict[str, Any], fecha_entrega: str) -> dict[str, Any]:
    if _activo_to_bool(order.get("venta_registrada", False)):
        return {"venta_registrada": True, "stock_reservado": False}

    items = get_order_items(str(order["id"]))
    _register_sale(order, items, fecha_entrega)
    return {"venta_registrada": True, "stock_reservado": False}


def _apply_revierte_venta(order: dict[str, Any]) -> dict[str, Any]:
    items = get_order_items(str(order["id"]))
    venta_registrada = _activo_to_bool(order.get("venta_registrada", False))
    stock_reservado = _activo_to_bool(order.get("stock_reservado", False))

    if venta_registrada:
        delete_sales_by_pedido(str(order["id"]))
        _release_stock(items)
        return {"venta_registrada": False, "stock_reservado": False}

    if stock_reservado:
        _release_stock(items)
        return {"stock_reservado": False}

    return {}


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
    _reserve_stock(normalized_items)

    db = get_db()
    timestamp = now_iso()
    initial_state = get_initial_order_state_name()

    order = {
        "id": new_id("PED"),
        "cliente_id": cliente_id,
        "cliente_nombre": cliente_nombre,
        "total": total,
        "estado": initial_state,
        "venta_registrada": False,
        "stock_reservado": True,
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
    old_items = get_order_items(order_id)
    normalized_items, total = _normalize_items(items)

    if _activo_to_bool(order.get("stock_reservado", False)):
        _release_stock(old_items)
        _reserve_stock(normalized_items)

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

    if _activo_to_bool(order.get("stock_reservado", False)):
        _release_stock(get_order_items(order_id))

    get_db().delete_by_id(TABLE_PEDIDOS, order_id)
    return True


def update_order_status(
    order_id: str,
    new_status: str,
    fecha_entrega: str | None = None,
) -> bool:
    valid_states = order_state_names(active_only=True)
    if new_status not in valid_states:
        raise ValueError(f"Estado inválido. Usa uno de: {', '.join(valid_states)}")

    order = get_order(order_id)
    if order is None:
        return False

    allowed = get_allowed_next_states(order)
    if new_status not in allowed and str(order.get("estado", "")) != new_status:
        raise ValueError("Transición de estado no permitida para este pedido.")

    state_config = get_order_state_by_name(new_status)
    if state_config is None:
        raise ValueError("Estado de pedido no configurado.")

    updates: dict[str, Any] = {
        "estado": new_status,
        "fecha_actualizacion": now_iso(),
    }

    if _activo_to_bool(state_config.get("genera_venta", False)):
        if not fecha_entrega:
            raise ValueError("Debe indicar la fecha y hora de registro de la venta.")
        updates.update(_apply_genera_venta(order, fecha_entrega))
        updates["fecha_entrega"] = fecha_entrega

    if _activo_to_bool(state_config.get("revierte_venta", False)):
        updates.update(_apply_revierte_venta(order))
        updates["fecha_entrega"] = None

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
            "talla": row.get("talla", "") or "",
            "cantidad": row["cantidad"],
            "precio_unitario": row["precio_unitario"],
            "subtotal": row["subtotal"],
        }
        for row in rows
    ]


def list_editable_orders() -> pd.DataFrame:
    df = list_orders()
    if df.empty:
        return df
    return df[~df["estado"].astype(str).map(order_state_blocks_editing)]


def state_requires_sale_date(state_name: str) -> bool:
    config = get_order_state_by_name(state_name)
    if config is None:
        return False
    return _activo_to_bool(config.get("genera_venta", False))
