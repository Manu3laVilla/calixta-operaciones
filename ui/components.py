from __future__ import annotations

import html
from contextlib import contextmanager
from typing import Any, Generator

import pandas as pd
import streamlit as st

from ui.search_autocomplete import CLEAR_VALUE, calixta_autocomplete

DEFAULT_TABLE_PAGE_SIZE = 10


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-hero">
            <h1 class="page-title">{html.escape(title)}</h1>
            <p class="page-subtitle">{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def page_section() -> Generator[None, None, None]:
    """Contenedor visual consistente para pantallas secundarias."""
    with st.container(border=True):
        st.markdown('<div class="page-section-inner">', unsafe_allow_html=True)
        yield
        st.markdown("</div>", unsafe_allow_html=True)


def dashboard_welcome(
    title: str = "Hola, Calixta!",
    subtitle: str = "Aquí tienes un resumen de tu negocio.",
) -> None:
    st.markdown(
        f"""
        <div class="welcome-block">
            <h1 class="welcome-title">{html.escape(title)}</h1>
            <p class="welcome-sub">{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _stat_chip(label: str, value: str, detail: str, variant: str) -> None:
    st.markdown(
        f"""
        <div class="stat-chip stat-chip--{html.escape(variant)}">
            <span class="stat-chip-label">{html.escape(label)}</span>
            <span class="stat-chip-value">{html.escape(value)}</span>
            <span class="stat-chip-detail">{html.escape(detail)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_chips(items: list[tuple[str, str, str, str]], *, bottom_gap: bool = True) -> None:
    """(etiqueta, valor, detalle, variante)."""
    cols = st.columns(len(items), gap="medium")
    for col, (label, value, detail, variant) in zip(cols, items):
        with col:
            _stat_chip(label, value, detail, variant)
    if bottom_gap:
        st.markdown('<div class="metrics-charts-gap" aria-hidden="true"></div>', unsafe_allow_html=True)


def summary_stats(items: list[tuple[str, str]]) -> None:
    rows = "".join(
        f'<div class="summary-stat"><span>{html.escape(l)}</span><strong>{html.escape(v)}</strong></div>'
        for l, v in items
    )
    st.markdown(f'<div class="summary-panel">{rows}</div>', unsafe_allow_html=True)


@contextmanager
def panel_card(title: str, *, accent: str = "olive") -> Generator[None, None, None]:
    with st.container(border=True):
        st.markdown(
            f'<p class="panel-heading panel-heading--{html.escape(accent)}">{html.escape(title)}</p>',
            unsafe_allow_html=True,
        )
        yield


def quick_item(title: str, subtitle: str, *, accent: str = "olive") -> None:
    st.markdown(
        f"""
        <div class="quick-item quick-item--{html.escape(accent)}">
            <div class="quick-item-text">
                <strong>{html.escape(title)}</strong>
                <span>{html.escape(subtitle)}</span>
            </div>
            <span class="quick-item-arrow">›</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_row(label: str, pct: int, *, color: str = "olive") -> None:
    pct = max(0, min(100, pct))
    st.markdown(
        f"""
        <div class="progress-row">
            <div class="progress-row-head">
                <span>{html.escape(label)}</span>
                <span>{pct}%</span>
            </div>
            <div class="progress-track">
                <div class="progress-fill progress-fill--{html.escape(color)}" style="width:{pct}%"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(items: list[tuple[str, str, str]]) -> None:
    stat_chips([(l, v, "", c) for l, v, c in items])


def chart_card(title: str) -> None:
    st.markdown(f'<p class="panel-heading">{html.escape(title)}</p>', unsafe_allow_html=True)


def chart_card_end() -> None:
    pass


def search_select(
    label: str,
    options: dict[str, Any],
    *,
    key: str,
    placeholder: str = "Escribe para buscar…",
    default_label: str | None = None,
    max_results: int = 12,
    help: str | None = None,
) -> Any | None:
    """Autocompletado integrado: escribe, filtra al instante y elige de la lista."""
    if not options:
        st.caption("No hay opciones disponibles.")
        return None

    labels = list(options.keys())
    confirmed_key = f"{key}__confirmed"
    reset_token = st.session_state.get(f"{key}__reset", 0)

    if default_label in options and confirmed_key not in st.session_state:
        st.session_state[confirmed_key] = default_label

    if help:
        st.caption(help)

    picked = calixta_autocomplete(
        label=label,
        options=labels,
        key=key,
        placeholder=placeholder,
        default=st.session_state.get(confirmed_key, default_label or ""),
        max_results=max_results,
        reset_token=reset_token,
    )

    if picked == CLEAR_VALUE:
        st.session_state.pop(confirmed_key, None)
        return None

    if picked in options:
        st.session_state[confirmed_key] = picked

    confirmed = st.session_state.get(confirmed_key)
    if confirmed in options:
        return options[confirmed]

    return None


def clear_search_select(*keys: str) -> None:
    """Reinicia buscadores tras guardar o cancelar una edición."""
    for key in keys:
        st.session_state.pop(f"{key}__confirmed", None)
        st.session_state.pop(key, None)
        st.session_state[f"{key}__reset"] = st.session_state.get(f"{key}__reset", 0) + 1


def calixta_table(
    data: pd.DataFrame,
    *,
    key: str,
    page_size: int = DEFAULT_TABLE_PAGE_SIZE,
    paginate: bool = True,
    **kwargs: Any,
) -> None:
    """Tabla con estilo Calixta y paginación (10 registros por página por defecto)."""
    if data.empty:
        return

    total = len(data)
    page_state_key = f"calixta_table_page__{key}"
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = int(st.session_state.get(page_state_key, 0))

    if page >= total_pages:
        page = 0
        st.session_state[page_state_key] = 0

    if paginate and total > page_size:
        start = page * page_size
        view = data.iloc[start : start + page_size]
    else:
        view = data

    st.markdown(
        f'<div class="calixta-table-frame" data-table-key="{html.escape(key)}"></div>',
        unsafe_allow_html=True,
    )
    st.dataframe(view, use_container_width=True, hide_index=True, **kwargs)

    if paginate and total > page_size:
        prev_col, meta_col, next_col = st.columns([1.1, 2.2, 1.1], gap="small")
        with prev_col:
            if st.button(
                "← Anterior",
                key=f"{key}_prev",
                disabled=page <= 0,
                use_container_width=True,
                type="secondary",
            ):
                st.session_state[page_state_key] = max(0, page - 1)
                st.rerun()
        with meta_col:
            st.markdown(
                (
                    f'<p class="calixta-table-meta">Página '
                    f"<strong>{page + 1}</strong> de <strong>{total_pages}</strong> · "
                    f"{total} registros</p>"
                ),
                unsafe_allow_html=True,
            )
        with next_col:
            if st.button(
                "Siguiente →",
                key=f"{key}_next",
                disabled=page >= total_pages - 1,
                use_container_width=True,
                type="secondary",
            ):
                st.session_state[page_state_key] = min(total_pages - 1, page + 1)
                st.rerun()
