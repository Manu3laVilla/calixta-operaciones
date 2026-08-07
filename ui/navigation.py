from __future__ import annotations

from pathlib import Path

import streamlit as st

from ui.cached_data import clear_data_cache, load_low_stock_alerts
from ui.theme import LOGO_PATH

MENU_PAGES: list[tuple[str, str, str]] = [
    ("Inicio", "dashboard", "◆"),
    ("Productos", "productos", "▦"),
    ("Clientes", "clientes", "◎"),
    ("Pedidos", "pedidos", "▤"),
    ("Ventas", "ventas", "◇"),
    ("Alertas", "alertas", "!"),
]

PAGE_IDS = [page_id for _, page_id, _ in MENU_PAGES]


def _alert_count() -> int:
    try:
        return len(load_low_stock_alerts())
    except Exception:
        return 0


def _label_for_page(page_id: str, alerts: int) -> str:
    for label, pid, _ in MENU_PAGES:
        if pid != page_id:
            continue
        if pid == "dashboard":
            return "Inicio"
        if pid == "alertas":
            return f"Alertas ({alerts})" if alerts > 0 else "Alertas"
        return label
    return page_id


def _mobile_label(page_id: str, alerts: int) -> str:
    for label, pid, icon in MENU_PAGES:
        if pid != page_id:
            continue
        text = label
        if pid == "alertas" and alerts > 0:
            text = f"{label}\n({alerts})"
        return f"{icon}\n{text}"
    return page_id


def _go_to_page(page_id: str) -> None:
    st.session_state.nav_page = page_id


def _refresh_data() -> None:
    clear_data_cache()


def _render_logo() -> None:
    logo = Path(LOGO_PATH)
    if logo.exists():
        st.image(str(logo), width=130)
    else:
        st.markdown('<p class="nav-logo-fallback">calixta</p>', unsafe_allow_html=True)


def _render_desktop_nav(current_page: str, alerts: int) -> None:
    st.markdown('<div id="desktop-nav-anchor"></div>', unsafe_allow_html=True)
    cols = st.columns(len(MENU_PAGES))
    for col, (label, page_id, icon) in zip(cols, MENU_PAGES):
        with col:
            text = _label_for_page(page_id, alerts)
            st.button(
                f"{icon}  {text}",
                key=f"desk_nav_{page_id}",
                use_container_width=True,
                type="primary" if page_id == current_page else "secondary",
                on_click=_go_to_page,
                args=(page_id,),
            )


def _render_mobile_nav(current_page: str, alerts: int) -> None:
    st.markdown('<div id="mobile-nav-anchor"></div>', unsafe_allow_html=True)
    cols = st.columns(len(MENU_PAGES))
    for col, (label, page_id, icon) in zip(cols, MENU_PAGES):
        with col:
            st.button(
                _mobile_label(page_id, alerts),
                key=f"mob_nav_{page_id}",
                use_container_width=True,
                type="primary" if page_id == current_page else "secondary",
                on_click=_go_to_page,
                args=(page_id,),
            )


def render_navigation() -> str:
    alerts = _alert_count()

    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "dashboard"

    if st.session_state.nav_page not in PAGE_IDS:
        st.session_state.nav_page = "dashboard"

    current_page = st.session_state.nav_page

    st.markdown('<div class="calixta-nav-shell">', unsafe_allow_html=True)

    top_left, top_center, top_right = st.columns([1.4, 4.2, 0.7])
    with top_left:
        _render_logo()
    with top_center:
        _render_desktop_nav(current_page, alerts)
    with top_right:
        st.button(
            "↻",
            key="nav_refresh",
            help="Actualizar datos",
            on_click=_refresh_data,
        )

    st.markdown("</div>", unsafe_allow_html=True)
    _render_mobile_nav(current_page, alerts)

    return current_page
