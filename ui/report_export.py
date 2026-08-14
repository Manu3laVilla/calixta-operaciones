"""Botones de exportación PDF en pantalla."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

import streamlit as st


def _render_download_button(
    *,
    label: str,
    file_name: str,
    builder: Callable[[], bytes],
    key: str,
    full_width: bool,
) -> None:
    st.download_button(
        label=label,
        data=builder(),
        file_name=file_name,
        mime="application/pdf",
        key=key,
        type="secondary",
        use_container_width=full_width,
    )


def pdf_download_button(
    *,
    label: str,
    file_name: str,
    builder: Callable[[], bytes],
    key: str,
    centered: bool = False,
) -> None:
    """Genera el PDF con los datos/filtros actuales y ofrece descarga."""
    wrap_key = f"{key}_pdf_wrap_center" if centered else f"{key}_pdf_wrap"

    if centered:
        st.markdown('<div class="pdf-download-spacer"></div>', unsafe_allow_html=True)
        with st.container(key=wrap_key):
            _, center, _ = st.columns([1, 1, 1], gap="medium")
            with center:
                _render_download_button(
                    label=label,
                    file_name=file_name,
                    builder=builder,
                    key=key,
                    full_width=True,
                )
        return

    with st.container(key=wrap_key):
        _render_download_button(
            label=label,
            file_name=file_name,
            builder=builder,
            key=key,
            full_width=False,
        )


def dated_filename(prefix: str) -> str:
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"{prefix}-{stamp}.pdf"


def filter_line(label: str, value: object | None) -> str:
    if value is None or value == "":
        return f"{label}: todos"
    return f"{label}: {value}"
