"""Carga configuración desde Streamlit Secrets (cloud) o .env (local)."""

from __future__ import annotations

import json
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


def get_google_credentials() -> dict[str, Any]:
    try:
        import streamlit as st

        if "gcp_service_account" in st.secrets:
            return dict(st.secrets["gcp_service_account"])
    except Exception:
        pass

    creds_path = get_env(
        "GOOGLE_CREDENTIALS_PATH",
        str(BASE_DIR / "credentials" / "service_account.json"),
    )
    path = Path(creds_path)
    if not path.exists():
        raise FileNotFoundError(
            "No se encontraron credenciales de Google. "
            "En local: guarda el JSON en credentials/service_account.json. "
            "En Streamlit Cloud: configura [gcp_service_account] en Secrets."
        )
    return json.loads(path.read_text(encoding="utf-8"))
