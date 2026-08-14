from __future__ import annotations

import base64
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import streamlit as st

from ui.cached_data import clear_data_cache, load_low_stock_alerts
from ui.theme import LOGO_PATH, NAV_ITEMS

PAGE_IDS = [page_id for _, page_id in NAV_ITEMS]

_LOGO_ROW = [1, 1.35, 1]
_NAV_ROW = [0.5, 11, 0.5]


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


def _mobile_header_html(current: str) -> str:
    menu_href = f"?p={current}&menu=1"
    return f"""
<div class="calixta-mobile-header-row">
  <a class="calixta-mobile-menu-link" href="{menu_href}" aria-label="Abrir menú">☰</a>
  <div class="calixta-mobile-header-logo">{_nav_logo_html()}</div>
</div>
"""


def _nav_logo_html() -> str:
    encoded = base64.b64encode(Path(LOGO_PATH).read_bytes()).decode("ascii")
    return (
        f'<div class="calixta-nav-logo">'
        f'<img src="data:image/png;base64,{encoded}" alt="Calixta" />'
        f"</div>"
    )


def _open_mobile_menu_if_requested(current: str, alerts: int) -> None:
    if _query_param("menu") != "1":
        return
    if "menu" in st.query_params:
        del st.query_params["menu"]
    _mobile_nav_dialog(current, alerts)


@st.dialog("Menú")
def _mobile_nav_dialog(current: str, alerts: int) -> None:
    for _, page_id in NAV_ITEMS:
        label = _nav_label(page_id, alerts)
        if st.button(
            label,
            key=f"nav_dialog_btn_{page_id}",
            type="primary" if page_id == current else "secondary",
            use_container_width=True,
        ):
            _go_to_page(page_id)
            st.rerun()


def _render_nav_bar(current: str, alerts: int) -> None:
    with st.container(key="calixta_nav"):
        st.markdown('<span class="calixta-nav-root" aria-hidden="true"></span>', unsafe_allow_html=True)

        with st.container(key="calixta_nav_logo_desktop"):
            logo_row = st.columns(_LOGO_ROW, gap="small")
            with logo_row[1]:
                st.markdown(_nav_logo_html(), unsafe_allow_html=True)

        with st.container(key="calixta_nav_mobile_header"):
            st.markdown(_mobile_header_html(current), unsafe_allow_html=True)

        with st.container(key="calixta_nav_desktop"):
            nav_row = st.columns(_NAV_ROW, gap="small", vertical_alignment="center")
            with nav_row[1]:
                tab_cols = st.columns([1] * len(NAV_ITEMS), gap="medium")
                for col, (_, page_id) in zip(tab_cols, NAV_ITEMS):
                    with col:
                        st.button(
                            _nav_label(page_id, alerts),
                            key=f"nav_btn_{page_id}",
                            type="primary" if page_id == current else "secondary",
                            use_container_width=False,
                            on_click=_go_to_page,
                            args=(page_id,),
                        )

    _open_mobile_menu_if_requested(current, alerts)


@contextmanager
def nav_layout() -> Generator[str, None, None]:
    alerts = _alert_count()
    current = _current_page()
    _render_nav_bar(current, alerts)
    try:
        yield current
    finally:
        pass
