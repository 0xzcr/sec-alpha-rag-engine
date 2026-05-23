from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from config import SQLITE_DB_PATH


@dataclass
class FinancialRecord:
    company: str
    fiscal_year: int
    total_revenue_musd: float
    net_income_musd: float
    total_assets_musd: float
    total_liabilities_musd: float
    cash_flow_from_operating_activities_musd: float


class StructuredStore:
    def __init__(self, sqlite_path: Path = SQLITE_DB_PATH, table_name: str = "financial_facts") -> None:
        self.sqlite_path = sqlite_path
        self.table_name = table_name

    def fetch_all(self) -> pd.DataFrame:
        with sqlite3.connect(self.sqlite_path) as connection:
            return pd.read_sql_query(f"SELECT * FROM {self.table_name}", connection)

    def fetch_company(self, company: str) -> pd.DataFrame:
        with sqlite3.connect(self.sqlite_path) as connection:
            query = f"SELECT * FROM {self.table_name} WHERE company = ? ORDER BY fiscal_year"
            return pd.read_sql_query(query, connection, params=(company,))

    def latest_year_value(self, company: str, column: str) -> Any:
        company_df = self.fetch_company(company)
        if company_df.empty:
            raise ValueError(f"No rows found for company: {company}")
        return company_df.iloc[-1][column]

    def yoy_change(self, company: str, column: str) -> float:
        company_df = self.fetch_company(company)
        if len(company_df) < 2:
            raise ValueError(f"Need at least 2 years for company: {company}")
        previous = float(company_df.iloc[-2][column])
        latest = float(company_df.iloc[-1][column])
        return ((latest - previous) / previous) * 100
