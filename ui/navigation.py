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


def _alert_count() -> int:
    try:
        return len(load_low_stock_alerts())
    except Exception:
        return 0


def _desktop_labels(alerts: int) -> list[str]:
    labels: list[str] = []
    for label, page_id, _ in MENU_PAGES:
        if page_id == "dashboard":
            labels.append("Dashboard")
        elif page_id == "alertas":
            labels.append(
                f"Alertas de stock ({alerts})" if alerts > 0 else "Alertas de stock"
            )
        else:
            labels.append(label)
    return labels


def _mobile_labels(alerts: int) -> list[str]:
    labels = []
    for label, page_id, icon in MENU_PAGES:
        text = label
        if page_id == "alertas" and alerts > 0:
            text = f"{label} ({alerts})"
        labels.append(f"{icon}\n{text}")
    return labels


def _page_index(page_id: str) -> int:
    for index, (_, pid, _) in enumerate(MENU_PAGES):
        if pid == page_id:
            return index
    return 0


def render_navigation() -> str:
    alerts = _alert_count()

    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "dashboard"

    current_idx = _page_index(st.session_state.nav_page)
    desktop_labels = _desktop_labels(alerts)
    mobile_labels = _mobile_labels(alerts)

    st.sidebar.markdown('<p class="brand-sidebar">Calixta</p>', unsafe_allow_html=True)
    st.sidebar.caption("Centro de Operaciones")

    sidebar_pick = st.sidebar.radio(
        "Menú",
        desktop_labels,
        index=current_idx,
        label_visibility="collapsed",
        key="nav_sidebar_pick",
    )
    sidebar_page = MENU_PAGES[desktop_labels.index(sidebar_pick)][1]

    st.sidebar.divider()
    if st.sidebar.button("Actualizar datos", use_container_width=True):
        clear_data_cache()
        st.rerun()
    st.sidebar.caption("Base de datos: Google Sheets")

    st.markdown(
        '<div class="mobile-top-bar"><p class="mobile-brand">Calixta</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="mobile-bottom-nav-anchor">', unsafe_allow_html=True)
    mobile_pick = st.radio(
        "Navegación móvil",
        mobile_labels,
        index=current_idx,
        horizontal=True,
        label_visibility="collapsed",
        key="nav_mobile_pick",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    mobile_page = MENU_PAGES[mobile_labels.index(mobile_pick)][1]

    new_page = st.session_state.nav_page
    if mobile_page != st.session_state.nav_page:
        new_page = mobile_page
    elif sidebar_page != st.session_state.nav_page:
        new_page = sidebar_page

    if new_page != st.session_state.nav_page:
        st.session_state.nav_page = new_page
        st.rerun()

    return st.session_state.nav_page
