from __future__ import annotations

import base64
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
            return f"Alertas · {alerts}"
        return label
    return page_id


def _img_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _brand_block() -> str:
    icon_uri = _img_data_uri(Path(ICON_PATH))
    logo_uri = _img_data_uri(Path(LOGO_PATH))
    icon_img = (
        f'<img src="{icon_uri}" alt="Calixta" class="brand-icon" />'
        if icon_uri
        else ""
    )
    logo_img = (
        f'<img src="{logo_uri}" alt="calixta" class="brand-logo" />'
        if logo_uri
        else '<span class="brand-fallback">calixta</span>'
    )
    return f"""
    <div class="brand-block">
        <div class="brand-icon-wrap">{icon_img}</div>
        <div class="brand-text">
            {logo_img}
            <span class="brand-subtitle">Centro de Operaciones</span>
        </div>
    </div>
    """


def render_navigation() -> str:
    alerts = _alert_count()

    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "dashboard"

    if st.session_state.nav_page not in PAGE_IDS:
        st.session_state.nav_page = "dashboard"

    st.markdown('<header class="site-header">', unsafe_allow_html=True)

    brand_col, action_col = st.columns([5.2, 0.8])
    with brand_col:
        st.markdown(_brand_block(), unsafe_allow_html=True)
    with action_col:
        if st.button("↻", key="nav_refresh", help="Actualizar datos"):
            clear_data_cache()
            st.rerun()

    selected = st.pills(
        "Sección",
        options=PAGE_IDS,
        format_func=lambda page_id: _nav_label(page_id, alerts),
        selection_mode="single",
        key="nav_page",
        label_visibility="collapsed",
        width="stretch",
    )

    st.markdown("</header>", unsafe_allow_html=True)

    if selected and selected in PAGE_IDS:
        return selected

    return st.session_state.nav_page
