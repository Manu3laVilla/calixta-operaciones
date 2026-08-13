"""Carga configuración desde Streamlit Secrets (cloud) o .env (local)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _streamlit_secret(key: str) -> Any | None:
    try:
        import streamlit as st

        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return None


def get_env(key: str, default: str = "") -> str:
    secret = _streamlit_secret(key)
    if secret is not None:
        return str(secret)
    return os.getenv(key, default)
