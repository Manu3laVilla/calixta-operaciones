from __future__ import annotations

from typing import Any

import pandas as pd

from config import (
    CATEGORIES,
    TABLE_CONTABILIDAD,
    TABLE_ESTADOS_PEDIDO,
    TABLE_PEDIDOS,
    TABLE_PRODUCTOS,
  TABLE_TIPOS_INGRESO,
  TABLE_TIPOS_GASTO,
  TABLE_TIPOS_PRODUCTO,
)
from services.supabase_db import get_db, new_id, now_iso


def _activo_to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("si", "sí", "true", "1", "yes")


def _sort_catalog(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if "nombre" in df.columns:
        return df.sort_values("nombre", ascending=True)
    return df


def _list_catalog(table: str, *, active_only: bool = False) -> pd.DataFrame:
    df = get_db().get_dataframe(table)
    if df.empty:
        return df
    if active_only and "activo" in df.columns:
        df = df[df["activo"].map(_activo_to_bool)]
    return _sort_catalog(df.copy())


def _ensure_unique_name(
    table: str,
    nombre: str,
    *,
    exclude_id: str | None = None,
    extra_filters: dict[str, Any] | None = None,
) -> None:
    df = get_db().get_dataframe(table)
    if df.empty:
        return

    nombre_norm = nombre.strip().casefold()
    for _, row in df.iterrows():
        if exclude_id and str(row.get("id")) == str(exclude_id):
            continue
        if extra_filters:
            if any(str(row.get(key)) != str(value) for key, value in extra_filters.items()):
                continue
        if str(row.get("nombre", "")).strip().casefold() == nombre_norm:
            raise ValueError(f"Ya existe un registro con el nombre «{nombre.strip()}».")


def _count_usage(table: str, column: str, value: str) -> int:
    df = get_db().get_dataframe(table)
    if df.empty or column not in df.columns:
        return 0
    return int((df[column].astype(str) == str(value)).sum())


# ── Tipos de producto ─────────────────────────────────────────────────────────

def list_product_types(
    *,
    categoria: str | None = None,
    active_only: bool = False,
) -> pd.DataFrame:
    df = _list_catalog(TABLE_TIPOS_PRODUCTO, active_only=active_only)
    if df.empty or not categoria:
        return df
    return df[df["categoria"].astype(str) == str(categoria)]


def get_product_type(type_id: str) -> dict[str, Any] | None:
    return get_db().get_by_id(TABLE_TIPOS_PRODUCTO, type_id)


def create_product_type(nombre: str, categoria: str) -> dict[str, Any]:
    nombre = nombre.strip()
    if categoria not in CATEGORIES:
        raise ValueError(f"Categoría inválida. Opciones: {', '.join(CATEGORIES)}")
    if not nombre:
        raise ValueError("El nombre es obligatorio.")

    _ensure_unique_name(
        TABLE_TIPOS_PRODUCTO,
        nombre,
        extra_filters={"categoria": categoria},
    )

    record = {
        "id": new_id("TPO"),
        "nombre": nombre,
        "categoria": categoria,
        "activo": True,
        "fecha_registro": now_iso(),
    }
    return get_db().insert(TABLE_TIPOS_PRODUCTO, record)


def update_product_type(type_id: str, updates: dict[str, Any]) -> bool:
    current = get_product_type(type_id)
    if current is None:
        return False

    payload = dict(updates)
    if "nombre" in payload:
        payload["nombre"] = str(payload["nombre"]).strip()
        if not payload["nombre"]:
            raise ValueError("El nombre es obligatorio.")
        categoria = str(payload.get("categoria", current.get("categoria", "")))
        _ensure_unique_name(
            TABLE_TIPOS_PRODUCTO,
            payload["nombre"],
            exclude_id=type_id,
            extra_filters={"categoria": categoria},
        )
    if "categoria" in payload and payload["categoria"] not in CATEGORIES:
        raise ValueError(f"Categoría inválida. Opciones: {', '.join(CATEGORIES)}")
    if "activo" in payload:
        payload["activo"] = _activo_to_bool(payload["activo"])

    return get_db().update_by_id(TABLE_TIPOS_PRODUCTO, type_id, payload)


def delete_product_type(type_id: str) -> bool:
    current = get_product_type(type_id)
    if current is None:
        return False

    in_use = _count_usage(TABLE_PRODUCTOS, "tipo_id", type_id)
    if in_use:
        raise ValueError(
            f"No se puede eliminar: {in_use} producto(s) usan este tipo. "
            "Desactívalo o reasigna los productos."
        )
    return get_db().delete_by_id(TABLE_TIPOS_PRODUCTO, type_id)


def product_type_options(
    categoria: str,
    *,
    active_only: bool = True,
) -> list[tuple[str, str]]:
    df = list_product_types(categoria=categoria, active_only=active_only)
    if df.empty:
        return []
    return [(str(row["nombre"]), str(row["id"])) for _, row in df.iterrows()]


# ── Tipos de ingreso ──────────────────────────────────────────────────────────

def list_income_types(*, active_only: bool = False) -> pd.DataFrame:
    return _list_catalog(TABLE_TIPOS_INGRESO, active_only=active_only)


def get_income_type(type_id: str) -> dict[str, Any] | None:
    return get_db().get_by_id(TABLE_TIPOS_INGRESO, type_id)


def create_income_type(nombre: str) -> dict[str, Any]:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio.")
    _ensure_unique_name(TABLE_TIPOS_INGRESO, nombre)

    record = {
        "id": new_id("TIN"),
        "nombre": nombre,
        "activo": True,
        "fecha_registro": now_iso(),
    }
    return get_db().insert(TABLE_TIPOS_INGRESO, record)


def update_income_type(type_id: str, updates: dict[str, Any]) -> bool:
    current = get_income_type(type_id)
    if current is None:
        return False

    payload = dict(updates)
    if "nombre" in payload:
        payload["nombre"] = str(payload["nombre"]).strip()
        if not payload["nombre"]:
            raise ValueError("El nombre es obligatorio.")
        _ensure_unique_name(TABLE_TIPOS_INGRESO, payload["nombre"], exclude_id=type_id)
    if "activo" in payload:
        payload["activo"] = _activo_to_bool(payload["activo"])

    db = get_db()
    old_name = str(current.get("nombre", ""))
    new_name = str(payload.get("nombre", old_name))
    if new_name != old_name:
        movements = db.get_dataframe(TABLE_CONTABILIDAD)
        if not movements.empty and "categoria" in movements.columns:
            for _, row in movements[movements["categoria"].astype(str) == old_name].iterrows():
                db.update_by_id(TABLE_CONTABILIDAD, str(row["id"]), {"categoria": new_name})

    return db.update_by_id(TABLE_TIPOS_INGRESO, type_id, payload)


def delete_income_type(type_id: str) -> bool:
    current = get_income_type(type_id)
    if current is None:
        return False

    nombre = str(current.get("nombre", ""))
    in_use = _count_usage(TABLE_CONTABILIDAD, "categoria", nombre)
    if in_use:
        raise ValueError(
            f"No se puede eliminar: {in_use} movimiento(s) usan este tipo. "
            "Desactívalo en su lugar."
        )
    return get_db().delete_by_id(TABLE_TIPOS_INGRESO, type_id)


def income_type_names(*, active_only: bool = True) -> list[str]:
    df = list_income_types(active_only=active_only)
    if df.empty:
        return []
    return [str(name) for name in df["nombre"].tolist()]


# ── Tipos de gasto ────────────────────────────────────────────────────────────

def list_expense_types(*, active_only: bool = False) -> pd.DataFrame:
    return _list_catalog(TABLE_TIPOS_GASTO, active_only=active_only)


def get_expense_type(type_id: str) -> dict[str, Any] | None:
    return get_db().get_by_id(TABLE_TIPOS_GASTO, type_id)


def create_expense_type(nombre: str) -> dict[str, Any]:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio.")
    _ensure_unique_name(TABLE_TIPOS_GASTO, nombre)

    record = {
        "id": new_id("TGA"),
        "nombre": nombre,
        "activo": True,
        "fecha_registro": now_iso(),
    }
    return get_db().insert(TABLE_TIPOS_GASTO, record)


def update_expense_type(type_id: str, updates: dict[str, Any]) -> bool:
    current = get_expense_type(type_id)
    if current is None:
        return False

    payload = dict(updates)
    if "nombre" in payload:
        payload["nombre"] = str(payload["nombre"]).strip()
        if not payload["nombre"]:
            raise ValueError("El nombre es obligatorio.")
        _ensure_unique_name(TABLE_TIPOS_GASTO, payload["nombre"], exclude_id=type_id)
    if "activo" in payload:
        payload["activo"] = _activo_to_bool(payload["activo"])

    db = get_db()
    old_name = str(current.get("nombre", ""))
    new_name = str(payload.get("nombre", old_name))
    if new_name != old_name:
        movements = db.get_dataframe(TABLE_CONTABILIDAD)
        if not movements.empty and "categoria" in movements.columns:
            expense_rows = movements[
                (movements["tipo"].astype(str) == "Gasto")
                & (movements["categoria"].astype(str) == old_name)
            ]
            for _, row in expense_rows.iterrows():
                db.update_by_id(TABLE_CONTABILIDAD, str(row["id"]), {"categoria": new_name})

    return db.update_by_id(TABLE_TIPOS_GASTO, type_id, payload)


def delete_expense_type(type_id: str) -> bool:
    current = get_expense_type(type_id)
    if current is None:
        return False

    nombre = str(current.get("nombre", ""))
    movements = get_db().get_dataframe(TABLE_CONTABILIDAD)
    if not movements.empty:
        in_use = int(
            (
                (movements["tipo"].astype(str) == "Gasto")
                & (movements["categoria"].astype(str) == nombre)
            ).sum()
        )
        if in_use:
            raise ValueError(
                f"No se puede eliminar: {in_use} movimiento(s) usan este tipo. "
                "Desactívalo en su lugar."
            )
    return get_db().delete_by_id(TABLE_TIPOS_GASTO, type_id)


def expense_type_names(*, active_only: bool = True) -> list[str]:
    df = list_expense_types(active_only=active_only)
    if df.empty:
        return []
    return [str(name) for name in df["nombre"].tolist()]


# ── Estados de pedido ─────────────────────────────────────────────────────────

def list_order_states(*, active_only: bool = False) -> pd.DataFrame:
    return _list_catalog(TABLE_ESTADOS_PEDIDO, active_only=active_only)


def get_order_state(state_id: str) -> dict[str, Any] | None:
    return get_db().get_by_id(TABLE_ESTADOS_PEDIDO, state_id)


def get_order_state_by_name(nombre: str) -> dict[str, Any] | None:
    df = get_db().get_dataframe(TABLE_ESTADOS_PEDIDO)
    if df.empty:
        return None
    match = df[df["nombre"].astype(str) == str(nombre)]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def create_order_state(
    nombre: str,
    *,
    genera_venta: bool = False,
    revierte_venta: bool = False,
    es_inicial: bool = False,
    bloquea_edicion: bool = False,
) -> dict[str, Any]:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio.")
    if genera_venta and revierte_venta:
        raise ValueError("Un estado no puede generar y revertir venta a la vez.")

    _ensure_unique_name(TABLE_ESTADOS_PEDIDO, nombre)

    db = get_db()
    if es_inicial:
        _clear_initial_state(db)

    record = {
        "id": new_id("EST"),
        "nombre": nombre,
        "activo": True,
        "genera_venta": bool(genera_venta),
        "revierte_venta": bool(revierte_venta),
        "es_inicial": bool(es_inicial),
        "bloquea_edicion": bool(bloquea_edicion),
        "fecha_registro": now_iso(),
    }
    return db.insert(TABLE_ESTADOS_PEDIDO, record)


def _clear_initial_state(db: Any, *, exclude_id: str | None = None) -> None:
    df = db.get_dataframe(TABLE_ESTADOS_PEDIDO)
    if df.empty:
        return
    for _, row in df.iterrows():
        if exclude_id and str(row.get("id")) == str(exclude_id):
            continue
        if row.get("es_inicial"):
            db.update_by_id(TABLE_ESTADOS_PEDIDO, str(row["id"]), {"es_inicial": False})


def update_order_state(state_id: str, updates: dict[str, Any]) -> bool:
    current = get_order_state(state_id)
    if current is None:
        return False

    payload = dict(updates)
    genera = payload.get("genera_venta", current.get("genera_venta", False))
    revierte = payload.get("revierte_venta", current.get("revierte_venta", False))
    if _activo_to_bool(genera) and _activo_to_bool(revierte):
        raise ValueError("Un estado no puede generar y revertir venta a la vez.")

    if "nombre" in payload:
        payload["nombre"] = str(payload["nombre"]).strip()
        if not payload["nombre"]:
            raise ValueError("El nombre es obligatorio.")
        _ensure_unique_name(TABLE_ESTADOS_PEDIDO, payload["nombre"], exclude_id=state_id)

    bool_fields = (
        "activo",
        "genera_venta",
        "revierte_venta",
        "es_inicial",
        "bloquea_edicion",
    )
    for field in bool_fields:
        if field in payload:
            payload[field] = _activo_to_bool(payload[field])

    db = get_db()
    if payload.get("es_inicial"):
        _clear_initial_state(db, exclude_id=state_id)

    old_name = str(current.get("nombre", ""))
    new_name = str(payload.get("nombre", old_name))
    if new_name != old_name:
        orders = db.get_dataframe(TABLE_PEDIDOS)
        if not orders.empty and "estado" in orders.columns:
            for _, row in orders[orders["estado"].astype(str) == old_name].iterrows():
                db.update_by_id(TABLE_PEDIDOS, str(row["id"]), {"estado": new_name})

    return db.update_by_id(TABLE_ESTADOS_PEDIDO, state_id, payload)


def delete_order_state(state_id: str) -> bool:
    current = get_order_state(state_id)
    if current is None:
        return False

    nombre = str(current.get("nombre", ""))
    in_use = _count_usage(TABLE_PEDIDOS, "estado", nombre)
    if in_use:
        raise ValueError(
            f"No se puede eliminar: {in_use} pedido(s) usan este estado. "
            "Desactívalo en su lugar."
        )
    if current.get("es_inicial"):
        raise ValueError("No se puede eliminar el estado inicial del flujo.")
    return get_db().delete_by_id(TABLE_ESTADOS_PEDIDO, state_id)


def order_state_names(*, active_only: bool = True) -> list[str]:
    df = list_order_states(active_only=active_only)
    if df.empty:
        return []
    return [str(name) for name in df["nombre"].tolist()]


def get_initial_order_state_name() -> str:
    df = list_order_states(active_only=True)
    if not df.empty and "es_inicial" in df.columns:
        initial = df[df["es_inicial"].map(_activo_to_bool)]
        if not initial.empty:
            return str(initial.iloc[0]["nombre"])
        return str(df.sort_values("nombre").iloc[0]["nombre"])
    return "Recibido"


def order_state_blocks_editing(estado: str) -> bool:
    config = get_order_state_by_name(estado)
    if config is None:
        return False
    return _activo_to_bool(config.get("bloquea_edicion", False))


def get_allowed_next_states(order: dict[str, Any]) -> list[str]:
    current_name = str(order.get("estado", ""))
    current = get_order_state_by_name(current_name)
    active = order_state_names(active_only=True)

    if current is None:
        return active

    venta_registrada = _activo_to_bool(order.get("venta_registrada", False))
    bloquea = _activo_to_bool(current.get("bloquea_edicion", False))
    revierte = _activo_to_bool(current.get("revierte_venta", False))

    if bloquea and revierte:
        return []

    if bloquea and venta_registrada:
        df = list_order_states(active_only=True)
        revert_states = df[df["revierte_venta"].map(_activo_to_bool)]["nombre"].tolist()
        return [str(name) for name in revert_states if str(name) != current_name]

    return [name for name in active if name != current_name]
