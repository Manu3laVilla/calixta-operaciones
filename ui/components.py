from __future__ import annotations

import html
from contextlib import contextmanager
from typing import Generator

import streamlit as st


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


def stat_chips(items: list[tuple[str, str, str, str]]) -> None:
    """(etiqueta, valor, detalle, variante)."""
    cols = st.columns(len(items), gap="small")
    for col, (label, value, detail, variant) in zip(cols, items):
        with col:
            _stat_chip(label, value, detail, variant)
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
