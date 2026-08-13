from __future__ import annotations

import utils.ssl_fix  # noqa: F401 — certificados SSL en Windows

import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

import pandas as pd
from supabase import Client, create_client

from utils.settings import get_env


class SupabaseDB:
    def __init__(self) -> None:
        self._client: Client | None = None

    def connect(self) -> Client:
        if self._client is not None:
            return self._client

        url = get_env("SUPABASE_URL", "").strip()
        key = get_env("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        if not url or not key:
            raise ValueError(
                "Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY. "
                "Configúralos en .env (local) o en Streamlit Secrets (cloud)."
            )

        self._client = create_client(url, key)
        return self._client

    @property
    def client(self) -> Client:
        return self.connect()

    def get_dataframe(self, table: str) -> pd.DataFrame:
        response = self.client.table(table).select("*").execute()
        rows = response.data or []
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows)

    def get_by_id(self, table: str, record_id: str) -> dict[str, Any] | None:
        response = (
            self.client.table(table)
            .select("*")
            .eq("id", str(record_id))
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    def insert(self, table: str, record: dict[str, Any]) -> dict[str, Any]:
        response = self.client.table(table).insert(record).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError(f"No se pudo insertar en {table}.")
        return rows[0]

    def update_by_id(
        self,
        table: str,
        record_id: str,
        updates: dict[str, Any],
    ) -> bool:
        response = (
            self.client.table(table)
            .update(updates)
            .eq("id", str(record_id))
            .execute()
        )
        return bool(response.data)

    def delete_by_id(self, table: str, record_id: str) -> bool:
        self.client.table(table).delete().eq("id", str(record_id)).execute()
        return True

    def select_where(
        self,
        table: str,
        *,
        column: str,
        value: Any,
    ) -> list[dict[str, Any]]:
        response = (
            self.client.table(table)
            .select("*")
            .eq(column, value)
            .execute()
        )
        return response.data or []

    def delete_where(
        self,
        table: str,
        *,
        column: str,
        value: Any,
    ) -> None:
        self.client.table(table).delete().eq(column, value).execute()

    def insert_many(self, table: str, records: list[dict[str, Any]]) -> None:
        if not records:
            return
        self.client.table(table).insert(records).execute()


@lru_cache(maxsize=1)
def get_db() -> SupabaseDB:
    return SupabaseDB()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
