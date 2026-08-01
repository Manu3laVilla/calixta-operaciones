"""Capa de caché para reducir lecturas a Google Sheets."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st

from services.alert_service import get_low_stock_alerts as _get_low_stock_alerts
from services.customer_service import list_customers as _list_customers
from services.order_service import list_orders as _list_orders
from services.product_service import list_products as _list_products
from services.sale_service import list_sales as _list_sales

CACHE_TTL = 60


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_products(active_only: bool = False) -> pd.DataFrame:
    return _list_products(active_only=active_only)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_customers() -> pd.DataFrame:
    return _list_customers()


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_sales() -> pd.DataFrame:
    return _list_sales()


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_orders() -> pd.DataFrame:
    return _list_orders()


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_low_stock_alerts() -> pd.DataFrame:
    return _get_low_stock_alerts()


def clear_data_cache() -> None:
    load_products.clear()
    load_customers.clear()
    load_sales.clear()
    load_orders.clear()
    load_low_stock_alerts.clear()


def filter_sales(
    sales: pd.DataFrame,
    cliente_id: str | None = None,
    producto_id: str | None = None,
    pedido_id: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
) -> pd.DataFrame:
    if sales.empty:
        return sales

    df = sales.copy()
    if cliente_id:
        df = df[df["cliente_id"].astype(str) == str(cliente_id)]
    if producto_id:
        df = df[df["producto_id"].astype(str) == str(producto_id)]
    if pedido_id:
        df = df[df["pedido_id"].astype(str) == str(pedido_id)]
    if fecha_desde and "fecha_entrega" in df.columns:
        df = df[df["fecha_entrega"].astype(str) >= fecha_desde]
    if fecha_hasta and "fecha_entrega" in df.columns:
        df = df[df["fecha_entrega"].astype(str) <= fecha_hasta]

    if "fecha_entrega" in df.columns:
        return df.sort_values("fecha_entrega", ascending=False)
    return df


def get_order_items_cached(order_id: str) -> list[dict[str, Any]]:
    orders = load_orders()
    if orders.empty:
        return []

    match = orders[orders["id"].astype(str) == str(order_id)]
    if match.empty:
        return []

    items_json = str(match.iloc[0].get("items_json", ""))
    if not items_json:
        return []

    try:
        items = json.loads(items_json)
        return items if isinstance(items, list) else []
    except json.JSONDecodeError:
        return []
