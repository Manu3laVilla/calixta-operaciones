from __future__ import annotations

from pathlib import Path

import streamlit as st

from ui.cached_data import clear_data_cache, load_low_stock_alerts
from ui.theme import LOGO_PATH

MENU_PAGES: list[tuple[str, str, str]] = [
    ("Inicio", "dashboard"),
    ("Productos", "productos"),
    ("Clientes", "clientes"),
    ("Pedidos", "pedidos"),
    ("Ventas", "ventas"),
    ("Alertas", "alertas"),
]

PAGE_IDS = [page_id for _, page_id in MENU_PAGES]


def _alert_count() -> int:
    try:
        return len(load_low_stock_alerts())
    except Exception:
        return 0


def _nav_label(page_id: str, alerts: int) -> str:
    for label, pid in MENU_PAGES:
        if pid != page_id:
            continue
        if pid == "alertas" and alerts > 0:
            return f"Alertas · {alerts}"
        return label
    return page_id


def render_navigation() -> str:
    alerts = _alert_count()

    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "dashboard"

    if st.session_state.nav_page not in PAGE_IDS:
        st.session_state.nav_page = "dashboard"

    st.markdown('<header class="site-header">', unsafe_allow_html=True)

    logo_col, tagline_col, action_col = st.columns([1.2, 3.3, 0.8])
    with logo_col:
        logo = Path(LOGO_PATH)
        if logo.exists():
            st.image(str(logo), width=108)
        else:
            st.markdown('<span class="logo-fallback">calixta</span>', unsafe_allow_html=True)

    with tagline_col:
        st.markdown(
            '<p class="site-tagline">Centro de Operaciones</p>',
            unsafe_allow_html=True,
        )

    with action_col:
        if st.button("Actualizar", key="nav_refresh", use_container_width=True):
            clear_data_cache()
            st.rerun()

    st.radio(
        "Sección",
        options=PAGE_IDS,
        format_func=lambda page_id: _nav_label(page_id, alerts),
        horizontal=True,
        key="nav_page",
        label_visibility="collapsed",
    )

    st.markdown("</header>", unsafe_allow_html=True)

    return st.session_state.nav_page
