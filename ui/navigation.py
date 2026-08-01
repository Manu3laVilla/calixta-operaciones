from __future__ import annotations

import streamlit as st

from ui.cached_data import clear_data_cache, load_low_stock_alerts

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
            return "Dashboard"
        if pid == "alertas":
            return f"Alertas de stock ({alerts})" if alerts > 0 else "Alertas de stock"
        return label
    return page_id


def _mobile_label_for_page(page_id: str, alerts: int) -> str:
    for label, pid, icon in MENU_PAGES:
        if pid != page_id:
            continue
        text = label
        if pid == "alertas" and alerts > 0:
            text = f"{label} ({alerts})"
        return f"{icon}\n{text}"
    return page_id


def _go_to_page(page_id: str) -> None:
    st.session_state.nav_page = page_id
    st.session_state.nav_sidebar = page_id


def _render_mobile_nav(current_page: str, alerts: int) -> None:
    st.markdown('<div id="mobile-nav-anchor"></div>', unsafe_allow_html=True)
    cols = st.columns(len(MENU_PAGES))
    for col, (label, page_id, icon) in zip(cols, MENU_PAGES):
        with col:
            st.button(
                _mobile_label_for_page(page_id, alerts),
                key=f"nav_btn_{page_id}",
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

    if "nav_sidebar" not in st.session_state:
        st.session_state.nav_sidebar = st.session_state.nav_page

    if st.session_state.nav_sidebar not in PAGE_IDS:
        st.session_state.nav_sidebar = st.session_state.nav_page

    st.sidebar.markdown('<p class="brand-sidebar">Calixta</p>', unsafe_allow_html=True)
    st.sidebar.caption("Centro de Operaciones")

    st.sidebar.radio(
        "Menú",
        options=PAGE_IDS,
        format_func=lambda page_id: _label_for_page(page_id, alerts),
        key="nav_sidebar",
        label_visibility="collapsed",
    )

    st.sidebar.divider()
    if st.sidebar.button("Actualizar datos", use_container_width=True):
        clear_data_cache()
        st.rerun()
    st.sidebar.caption("Base de datos: Google Sheets")

    st.session_state.nav_page = st.session_state.nav_sidebar
    current_page = st.session_state.nav_page

    st.markdown(
        '<div class="mobile-top-bar"><p class="mobile-brand">Calixta</p></div>',
        unsafe_allow_html=True,
    )
    _render_mobile_nav(current_page, alerts)

    return current_page
