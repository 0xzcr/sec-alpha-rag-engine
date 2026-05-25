from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path

import pandas as pd

from config import (
    COMPANY_TICKERS,
    CONCEPT_ALIASES,
    CONSOLIDATED_TABLE_PATH,
    END_YEAR,
    METRIC_COLUMNS,
    SEC_COMPANY_FACTS_DIR,
    SQLITE_DB_PATH,
    START_YEAR,
    STRUCTURED_OUTPUT_ROOT,
    SUMMARY_TABLE_PATH,
)


def load_companyfacts_payloads() -> list[tuple[str, dict]]:
    if not SEC_COMPANY_FACTS_DIR.exists():
        raise FileNotFoundError(
            f"Company facts directory not found at {SEC_COMPANY_FACTS_DIR}. "
            "Run 01_ingest first."
        )

    payloads: list[tuple[str, dict]] = []
    for company, ticker in COMPANY_TICKERS.items():
        facts_path = SEC_COMPANY_FACTS_DIR / f"{ticker.lower()}.json"
        if not facts_path.exists():
            raise FileNotFoundError(
                f"Missing company facts payload for {company}: {facts_path}"
            )
        payloads.append((company, json.loads(facts_path.read_text(encoding="utf-8"))))
    return payloads


def _parse_date(value: str | None) -> str:
    if not value:
        return ""
    return str(value)


def _coerce_millions(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value) / 1_000_000.0
    except (TypeError, ValueError):
        return None


def _score_fact(entry: dict) -> tuple:
    filed = entry.get("filed") or ""
    fp = str(entry.get("fp") or "").upper()
    form = str(entry.get("form") or "")
    form_priority = 1 if form == "10-K" else 0
    fp_priority = 1 if fp == "FY" else 0
    return (
        form_priority,
        fp_priority,
        filed,
        str(entry.get("end") or ""),
    )


def _find_metric_fact(payload: dict, year: int, aliases: list[str]) -> dict | None:
    facts = payload.get("facts", {})
    candidate_rows: list[dict] = []

    for taxonomy_name, taxonomy in facts.items():
        if not isinstance(taxonomy, dict):
            continue
        for concept_name, concept in taxonomy.items():
            if concept_name not in aliases:
                continue
            units = concept.get("units", {})
            if not isinstance(units, dict):
                continue
            for unit_name, entries in units.items():
                if not isinstance(entries, list):
                    continue
                if not str(unit_name).upper().startswith("USD"):
                    continue
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    if int(entry.get("fy") or -1) != year:
                        continue
                    if str(entry.get("form") or "") not in {"10-K", "10-K/A"}:
                        continue
                    if str(entry.get("fp") or "").upper() not in {"FY", "FYR"}:
                        continue
                    value = _coerce_millions(entry.get("val"))
                    if value is None:
                        continue
                    candidate_rows.append(
                        {
                            "value_musd": round(value, 2),
                            "concept": concept_name,
                            "taxonomy": taxonomy_name,
                            "unit": unit_name,
                            "fy": int(entry.get("fy") or year),
                            "period_end": _parse_date(entry.get("end")),
                            "filed": _parse_date(entry.get("filed")),
                            "form": str(entry.get("form") or ""),
                            "frame": str(entry.get("frame") or ""),
                            "accn": str(entry.get("accn") or ""),
                        }
                    )

    if not candidate_rows:
        return None

    candidate_rows.sort(key=lambda item: _score_fact(item), reverse=True)
    best = candidate_rows[0]
    return best


def extract_company_rows(company: str, ticker: str, payload: dict) -> list[dict]:
    rows: list[dict] = []
    for year in range(START_YEAR, END_YEAR + 1):
        row = {
            "company": company,
            "ticker": ticker,
            "fiscal_year": year,
            "period_end": None,
            "source_file": f"{ticker.lower()}.json",
        }

        metric_found = False
        for metric_name in METRIC_COLUMNS:
            fact = _find_metric_fact(payload, year, CONCEPT_ALIASES[metric_name])
            if fact is None:
                row[metric_name] = None
                row[f"{metric_name}_source_concept"] = ""
                row[f"{metric_name}_source_form"] = ""
                continue

            metric_found = True
            row[metric_name] = fact["value_musd"]
            row[f"{metric_name}_source_concept"] = fact["concept"]
            row[f"{metric_name}_source_form"] = fact["form"]
            if row["period_end"] is None:
                row["period_end"] = fact["period_end"]

        if metric_found:
            rows.append(row)

    return rows


def build_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["company", *METRIC_COLUMNS])

    summary = (
        df.groupby("company")[METRIC_COLUMNS]
        .agg(["mean", "min", "max", "std"])
        .round(2)
    )
    summary.columns = [
        "_".join(column).strip() for column in summary.columns.to_flat_index()
    ]
    return summary.reset_index()


def write_sqlite_table(df: pd.DataFrame, table_name: str = "financial_facts") -> None:
    STRUCTURED_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(SQLITE_DB_PATH) as connection:
        df.to_sql(table_name, connection, if_exists="replace", index=False)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    payloads = load_companyfacts_payloads()

    all_rows: list[dict] = []
    for company, payload in payloads:
        ticker = COMPANY_TICKERS[company]
        all_rows.extend(extract_company_rows(company, ticker, payload))

    if not all_rows:
        raise RuntimeError("No structured facts could be extracted from SEC payloads.")

    enriched = pd.DataFrame(all_rows).sort_values(
        ["company", "fiscal_year"]
    ).reset_index(drop=True)

    for column in METRIC_COLUMNS:
        enriched[column] = pd.to_numeric(enriched[column], errors="coerce")

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

    summary = build_summary_table(enriched)

    write_jsonl(CONSOLIDATED_TABLE_PATH, enriched.to_dict(orient="records"))
    SUMMARY_TABLE_PATH.write_text(
        json.dumps(summary.to_dict(orient="records"), indent=2),
        encoding="utf-8",
    )
    write_sqlite_table(enriched)

    print(f"Structured store written to {STRUCTURED_OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
