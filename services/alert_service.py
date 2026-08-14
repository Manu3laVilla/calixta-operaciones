from __future__ import annotations

import pandas as pd

from services.alert_config_service import get_active_alert_recipient_emails
from services.product_service import list_products


def get_low_stock_alerts() -> pd.DataFrame:
    products = list_products(active_only=True)
    if products.empty:
        return products

    alerts = products[products["stock"] <= products["stock_minimo"]].copy()
    if alerts.empty:
        return alerts

    alerts["faltante"] = alerts["stock_minimo"] - alerts["stock"]
    sort_cols = [c for c in ["faltante", "stock"] if c in alerts.columns]
    return alerts.sort_values(sort_cols, ascending=[False, True] if len(sort_cols) == 2 else [False])


def count_low_stock() -> int:
    alerts = get_low_stock_alerts()
    return len(alerts)


def notify_low_stock_by_email() -> int:
    from services.email_service import send_low_stock_alert

    alerts = get_low_stock_alerts()
    recipients = get_active_alert_recipient_emails()
    send_low_stock_alert(alerts, recipients=recipients or None)
    return len(alerts)
