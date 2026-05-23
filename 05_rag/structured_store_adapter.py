from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sqlite3
import sys
from typing import Any

import pandas as pd

MODULE_DIR = Path(__file__).resolve().parent


def _load_config():
    spec = spec_from_file_location("_rag_config", MODULE_DIR / "config.py")
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load 05_rag/config.py")
    module = module_from_spec(spec)
    sys.modules["_rag_config"] = module
    spec.loader.exec_module(module)
    return module


_config = _load_config()
STRUCTURED_STORE_PATH = _config.STRUCTURED_STORE_PATH
STRUCTURED_TABLE_NAME = _config.STRUCTURED_TABLE_NAME


class StructuredStoreAdapter:
    def __init__(self, sqlite_path: Path = STRUCTURED_STORE_PATH, table_name: str = STRUCTURED_TABLE_NAME) -> None:
        self.sqlite_path = sqlite_path
        self.table_name = table_name

    def fetch_company(self, company: str) -> pd.DataFrame:
        with sqlite3.connect(self.sqlite_path) as connection:
            query = f"SELECT * FROM {self.table_name} WHERE company = ? ORDER BY fiscal_year"
            return pd.read_sql_query(query, connection, params=(company,))

    def fetch_company_year(self, company: str, fiscal_year: int) -> pd.Series | None:
        company_df = self.fetch_company(company)
        match = company_df[company_df["fiscal_year"] == fiscal_year]
        if match.empty:
            return None
        return match.iloc[0]

    def fetch_all(self) -> pd.DataFrame:
        with sqlite3.connect(self.sqlite_path) as connection:
            return pd.read_sql_query(f"SELECT * FROM {self.table_name}", connection)

    def latest_row(self, company: str) -> dict[str, Any]:
        company_df = self.fetch_company(company)
        if company_df.empty:
            raise ValueError(f"No rows found for company: {company}")
        return company_df.iloc[-1].to_dict()

    def latest_value(self, company: str, column: str) -> Any:
        return self.latest_row(company)[column]

    def yoy_change(self, company: str, column: str) -> float:
        company_df = self.fetch_company(company)
        if len(company_df) < 2:
            raise ValueError(f"Need at least two years for {company}")
        previous = float(company_df.iloc[-2][column])
        latest = float(company_df.iloc[-1][column])
        return ((latest - previous) / previous) * 100
