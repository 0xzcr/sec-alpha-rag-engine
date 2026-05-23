from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from config import (
    CONSOLIDATED_TABLE_PATH,
    METRIC_COLUMNS,
    SQLITE_DB_PATH,
    STRUCTURED_INPUT_FILES,
    STRUCTURED_OUTPUT_ROOT,
    SUMMARY_TABLE_PATH,
)


def load_company_tables() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for csv_path in STRUCTURED_INPUT_FILES:
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing input CSV: {csv_path}")
        frame = pd.read_csv(csv_path)
        frame["source_file"] = csv_path.name
        frames.append(frame)

    combined = pd.concat(frames, ignore_index=True)
    combined["period_end"] = pd.to_datetime(combined["period_end"])
    combined = combined.sort_values(["company", "fiscal_year"]).reset_index(drop=True)
    return combined


def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    grouped = enriched.groupby("company", sort=True)

    for column in METRIC_COLUMNS:
        enriched[f"{column}_yoy_pct"] = grouped[column].pct_change() * 100

    enriched["profit_margin_pct"] = (
        enriched["net_income_musd"] / enriched["total_revenue_musd"] * 100
    )
    enriched["asset_liability_ratio"] = (
        enriched["total_assets_musd"] / enriched["total_liabilities_musd"]
    )
    enriched["operating_cash_flow_margin_pct"] = (
        enriched["cash_flow_from_operating_activities_musd"]
        / enriched["total_revenue_musd"]
        * 100
    )
    return enriched


def build_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("company")[METRIC_COLUMNS]
        .agg(["mean", "min", "max", "std"])
        .round(2)
    )
    summary.columns = ["_".join(column).strip() for column in summary.columns.to_flat_index()]
    summary = summary.reset_index()
    return summary


def write_sqlite_table(df: pd.DataFrame, table_name: str = "financial_facts") -> None:
    STRUCTURED_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(SQLITE_DB_PATH) as connection:
        df.to_sql(table_name, connection, if_exists="replace", index=False)


def main() -> None:
    STRUCTURED_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    combined = load_company_tables()
    enriched = add_derived_metrics(combined)
    summary = build_summary_table(enriched)

    enriched.to_csv(CONSOLIDATED_TABLE_PATH, index=False)
    summary.to_csv(SUMMARY_TABLE_PATH, index=False)
    write_sqlite_table(enriched)

    print(f"Structured store written to {STRUCTURED_OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
