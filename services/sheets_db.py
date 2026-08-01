from __future__ import annotations

import utils.ssl_fix  # noqa: F401

import uuid
from datetime import datetime
from functools import lru_cache
from typing import Any

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from config import SHEET_SCHEMAS, SPREADSHEET_ID
from utils.settings import get_google_credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SheetsDB:
    def __init__(self) -> None:
        self._client: gspread.Client | None = None
        self._spreadsheet: gspread.Spreadsheet | None = None

    def connect(self) -> gspread.Spreadsheet:
        if self._spreadsheet is not None:
            return self._spreadsheet

        if not SPREADSHEET_ID:
            raise ValueError(
                "Falta SPREADSHEET_ID. Configúralo en .env (local) "
                "o en Streamlit Secrets (cloud)."
            )

        credentials = Credentials.from_service_account_info(
            get_google_credentials(), scopes=SCOPES
        )
        self._client = gspread.authorize(credentials)
        self._spreadsheet = self._client.open_by_key(SPREADSHEET_ID)
        self._ensure_sheets()
        return self._spreadsheet

    def _ensure_sheets(self) -> None:
        assert self._spreadsheet is not None
        existing = {ws.title for ws in self._spreadsheet.worksheets()}

        for sheet_name, headers in SHEET_SCHEMAS.items():
            if sheet_name not in existing:
                worksheet = self._spreadsheet.add_worksheet(
                    title=sheet_name, rows=1000, cols=len(headers)
                )
                worksheet.append_row(headers)
            else:
                worksheet = self._spreadsheet.worksheet(sheet_name)
                current = worksheet.row_values(1)
                if not current:
                    worksheet.update("A1", [headers])
                elif current != headers:
                    missing = [h for h in headers if h not in current]
                    if missing:
                        worksheet.update("A1", [current + missing])

    def get_worksheet(self, name: str) -> gspread.Worksheet:
        spreadsheet = self.connect()
        return spreadsheet.worksheet(name)

    def get_records(self, sheet_name: str) -> list[dict[str, Any]]:
        worksheet = self.get_worksheet(sheet_name)
        records = worksheet.get_all_records()
        return [dict(row) for row in records]

    def get_dataframe(self, sheet_name: str) -> pd.DataFrame:
        records = self.get_records(sheet_name)
        if not records:
            headers = SHEET_SCHEMAS[sheet_name]
            return pd.DataFrame(columns=headers)
        return pd.DataFrame(records)

    def append_row(self, sheet_name: str, row: list[Any]) -> None:
        worksheet = self.get_worksheet(sheet_name)
        worksheet.append_row(row, value_input_option="USER_ENTERED")

    def update_row(self, sheet_name: str, row_number: int, row: list[Any]) -> None:
        worksheet = self.get_worksheet(sheet_name)
        headers = SHEET_SCHEMAS[sheet_name]
        cell_range = f"A{row_number}:{chr(64 + len(headers))}{row_number}"
        worksheet.update(cell_range, [row], value_input_option="USER_ENTERED")

    def find_row_number(self, sheet_name: str, id_field: str, record_id: str) -> int | None:
        worksheet = self.get_worksheet(sheet_name)
        headers = worksheet.row_values(1)
        if id_field not in headers:
            return None

        id_col = headers.index(id_field) + 1
        ids = worksheet.col_values(id_col)
        for index, value in enumerate(ids[1:], start=2):
            if str(value) == str(record_id):
                return index
        return None

    def delete_row(self, sheet_name: str, row_number: int) -> None:
        worksheet = self.get_worksheet(sheet_name)
        worksheet.delete_rows(row_number)


@lru_cache(maxsize=1)
def get_db() -> SheetsDB:
    return SheetsDB()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
