"""Capa de caché para reducir lecturas a Supabase."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from services.accounting_service import list_movements as _list_movements
from services.alert_service import get_low_stock_alerts as _get_low_stock_alerts
from services.alert_config_service import (
    get_alert_email_config as _get_alert_email_config,
    list_alert_recipients as _list_alert_recipients,
    list_alert_send_logs as _list_alert_send_logs,
)
from services.catalog_service import (
    list_expense_types as _list_expense_types,
    list_income_types as _list_income_types,
    list_order_states as _list_order_states,
    list_product_types as _list_product_types,
)
from services.customer_service import list_customers as _list_customers
from services.order_service import get_order_items as _get_order_items
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
def load_movements() -> pd.DataFrame:
    return _list_movements()


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_low_stock_alerts() -> pd.DataFrame:
    return _get_low_stock_alerts()


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_product_types(active_only: bool = False) -> pd.DataFrame:
    return _list_product_types(active_only=active_only)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_income_types(active_only: bool = False) -> pd.DataFrame:
    return _list_income_types(active_only=active_only)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_expense_types(active_only: bool = False) -> pd.DataFrame:
    return _list_expense_types(active_only=active_only)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_alert_email_config() -> dict:
    return _get_alert_email_config()


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_alert_recipients(active_only: bool = False) -> pd.DataFrame:
    return _list_alert_recipients(active_only=active_only)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_alert_send_logs(limit: int = 20) -> pd.DataFrame:
    return _list_alert_send_logs(limit=limit)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_order_states(active_only: bool = False) -> pd.DataFrame:
    return _list_order_states(active_only=active_only)


def clear_data_cache() -> None:
    load_products.clear()
    load_customers.clear()
    load_sales.clear()
    load_orders.clear()
    load_movements.clear()
    load_low_stock_alerts.clear()
    load_product_types.clear()
    load_income_types.clear()
    load_expense_types.clear()
    load_order_states.clear()
    load_alert_email_config.clear()
    load_alert_recipients.clear()
    load_alert_send_logs.clear()


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
    return _get_order_items(order_id)
