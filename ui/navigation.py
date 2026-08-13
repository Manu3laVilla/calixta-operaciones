from __future__ import annotations

import base64
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import streamlit as st

from ui.cached_data import clear_data_cache, load_low_stock_alerts
from ui.styles import CALIXTA_NAV_CSS
from ui.theme import LOGO_PATH, NAV_ITEMS
PAGE_IDS = [page_id for _, page_id in NAV_ITEMS]

_LOGO_ROW = [1, 1.35, 1]
_NAV_ROW = [0.1, 7.8, 0.38]

# Espaciado del header — inyectado aquí para que Streamlit cargue siempre la versión actual.
NAV_SPACING_CSS = """
<style id="calixta-nav-spacing">
section[data-testid="stMain"] .block-container > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
.st-key-calixta_nav {
    margin-top: 0 !important;
    padding-top: 0.35rem !important;
    overflow: visible !important;
}
.st-key-calixta_nav [data-testid="stElementContainer"]:has(.calixta-nav-root) {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
.st-key-calixta_nav .calixta-nav-logo {
    margin-bottom: 1.1rem !important;
    overflow: visible !important;
}
.st-key-calixta_nav .calixta-nav-logo img {
    overflow: visible !important;
}
</style>
"""


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


def _nav_logo_html() -> str:
    encoded = base64.b64encode(Path(LOGO_PATH).read_bytes()).decode("ascii")
    return (
        f'<div class="calixta-nav-logo">'
        f'<img src="data:image/png;base64,{encoded}" alt="Calixta" />'
        f"</div>"
    )


def _render_nav_bar(current: str, alerts: int) -> None:
    with st.container(key="calixta_nav"):
        st.markdown('<span class="calixta-nav-root" aria-hidden="true"></span>', unsafe_allow_html=True)

        logo_row = st.columns(_LOGO_ROW, gap="small")
        with logo_row[1]:
            st.markdown(_nav_logo_html(), unsafe_allow_html=True)
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

        with nav_row[2]:
            st.button(
                "↻",
                key="nav_refresh",
                help="Actualizar datos",
                on_click=_refresh_data,
            )

    st.markdown(CALIXTA_NAV_CSS, unsafe_allow_html=True)
    st.markdown(NAV_SPACING_CSS, unsafe_allow_html=True)


@contextmanager
def nav_layout() -> Generator[str, None, None]:
    alerts = _alert_count()
    current = _current_page()
    _render_nav_bar(current, alerts)
    try:
        yield current
    finally:
        pass
