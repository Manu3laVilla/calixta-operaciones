from __future__ import annotations

from pathlib import Path

import streamlit as st

from ui.cached_data import clear_data_cache, load_low_stock_alerts
from ui.theme import ICON_PATH, LOGO_PATH, NAV_ITEMS

PAGE_IDS = [page_id for _, page_id in NAV_ITEMS]


def _alert_count() -> int:
    try:
        return len(load_low_stock_alerts())
    except Exception:
        return 0


def _nav_label(page_id: str, alerts: int) -> str:
    for label, pid in NAV_ITEMS:
        if pid != page_id:
            continue
        if pid == "alertas" and alerts > 0:
            return f"{label} · {alerts}"
        return label
    return page_id


def render_navigation() -> str:
    alerts = _alert_count()

    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "dashboard"

    if st.session_state.nav_page not in PAGE_IDS:
        st.session_state.nav_page = "dashboard"

    st.markdown('<header class="glass-header">', unsafe_allow_html=True)

    brand_col, action_col = st.columns([5.5, 0.6])
    with brand_col:
        icon_path = Path(ICON_PATH)
        logo_path = Path(LOGO_PATH)
        if icon_path.exists() and logo_path.exists():
            i_col, l_col = st.columns([0.45, 1.55])
            with i_col:
                st.image(str(icon_path), width=38)
            with l_col:
                st.image(str(logo_path), width=94)
        elif logo_path.exists():
            st.image(str(logo_path), width=108)
        else:
            st.markdown('<span class="brand-fallback">calixta</span>', unsafe_allow_html=True)

    with action_col:
        if st.button("↻", key="nav_refresh", help="Actualizar datos", use_container_width=True):
            clear_data_cache()
            st.rerun()

    st.markdown('<nav class="glass-nav">', unsafe_allow_html=True)
    st.radio(
        "Sección",
        options=PAGE_IDS,
        format_func=lambda page_id: _nav_label(page_id, alerts),
        horizontal=True,
        key="nav_page",
        label_visibility="collapsed",
    )
    st.markdown("</nav></header>", unsafe_allow_html=True)

    return st.session_state.nav_page
