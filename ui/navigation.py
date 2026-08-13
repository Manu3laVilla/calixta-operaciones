from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

import streamlit as st

from ui.cached_data import clear_data_cache, load_low_stock_alerts
from ui.theme import LOGO_PATH, NAV_ITEMS

PAGE_IDS = [page_id for _, page_id in NAV_ITEMS]

_LOGO_WEIGHT = 0.72
_TAB_WEIGHT = 1.52
_REFRESH_WEIGHT = 0.34


def _alert_count() -> int:
    try:
        return len(load_low_stock_alerts())
    except Exception:
        return 0


def _nav_label(page_id: str, alerts: int) -> str:
    for label, pid in NAV_ITEMS:
        if pid == page_id:
            if pid == "alertas" and alerts > 0:
                return f"{label} ({alerts})"
            return label
    return page_id


def _go_to_page(page_id: str) -> None:
    st.session_state.nav_page = page_id
    st.query_params["p"] = page_id


def _refresh_data() -> None:
    clear_data_cache()


def _query_param(key: str) -> str | None:
    raw = st.query_params.get(key)
    if raw is None:
        return None
    if isinstance(raw, list):
        return str(raw[0]) if raw else None
    return str(raw)


def _current_page() -> str:
    page_from_url = _query_param("p")
    if page_from_url in PAGE_IDS:
        st.session_state.nav_page = page_from_url

    if _query_param("refresh") == "1":
        clear_data_cache()
        if "refresh" in st.query_params:
            del st.query_params["refresh"]

    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "dashboard"

    current = st.session_state.nav_page
    if current not in PAGE_IDS:
        current = "dashboard"
        st.session_state.nav_page = current
    return current


def _render_nav_bar(current: str, alerts: int) -> None:
    st.markdown('<span class="calixta-nav-root" aria-hidden="true"></span>', unsafe_allow_html=True)

    col_weights = [_LOGO_WEIGHT] + [_TAB_WEIGHT] * len(NAV_ITEMS) + [_REFRESH_WEIGHT]
    cols = st.columns(col_weights, gap="small", vertical_alignment="center")

    with cols[0]:
        st.image(LOGO_PATH, width=86)

    for col, (_, page_id) in zip(cols[1 : len(NAV_ITEMS) + 1], NAV_ITEMS):
        with col:
            st.button(
                _nav_label(page_id, alerts),
                key=f"nav_btn_{page_id}",
                type="primary" if page_id == current else "secondary",
                use_container_width=True,
                on_click=_go_to_page,
                args=(page_id,),
            )

    with cols[-1]:
        st.button(
            "↻",
            key="nav_refresh",
            help="Actualizar datos",
            on_click=_refresh_data,
        )


@contextmanager
def nav_layout() -> Generator[str, None, None]:
    alerts = _alert_count()
    current = _current_page()
    _render_nav_bar(current, alerts)
    try:
        yield current
    finally:
        pass
