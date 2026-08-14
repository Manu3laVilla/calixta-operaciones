from __future__ import annotations

import os

import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
_component = components.declare_component("calixta_autocomplete", path=_FRONTEND_DIR)

CLEAR_VALUE = "__CLEAR__"


def calixta_autocomplete(
    label: str,
    options: list[str],
    *,
    key: str | None = None,
    placeholder: str = "",
    default: str = "",
    max_results: int = 12,
    reset_token: int = 0,
) -> str | None:
    result = _component(
        label=label,
        options=options,
        placeholder=placeholder,
        defaultValue=default,
        max_results=max_results,
        reset_token=reset_token,
        key=key,
        default=None,
        height=78,
    )
    if result == CLEAR_VALUE:
        return CLEAR_VALUE
    if result:
        return str(result)
    return None
