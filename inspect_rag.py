from __future__ import annotations

from pathlib import Path
import sys

import sqlite3
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent
RAG_DIR = ROOT_DIR / "05_rag"
if str(RAG_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_DIR))

from query_planner import plan_query  # noqa: E402
from retrieval_adapter import RetrievalAdapter  # noqa: E402


INGEST_MANIFEST_PATH = ROOT_DIR / "data" / "raw" / "edgar" / "ingest_manifest.jsonl"
CHUNK_SUMMARY_PATH = ROOT_DIR / "data" / "processed" / "chunks" / "chunk_summary.jsonl"
STRUCTURED_DB_PATH = ROOT_DIR / "data" / "structured_store" / "financial_facts.sqlite"


def load_table(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_json(path, lines=True)


def load_sqlite_table(path: Path, table_name: str) -> pd.DataFrame | None:
    if not path.exists():
        return None
    with sqlite3.connect(path) as connection:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", connection)


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def summarize_ingest_manifest() -> None:
    df = load_table(INGEST_MANIFEST_PATH)
    print_section("Ingest Manifest")
    if df is None or df.empty:
        print(f"Missing or empty manifest: {INGEST_MANIFEST_PATH}")
        return

    print(f"Rows: {len(df)}")
    print(f"Companies: {', '.join(sorted(df['company'].unique()))}")
    print(f"Fiscal years: {int(df['filing_year'].min())} -> {int(df['filing_year'].max())}")
    print("\nBy company:")
    summary = df.groupby("company")["filing_year"].agg(["min", "max", "count"]).reset_index()
    print(summary.to_string(index=False))


def summarize_chunk_corpus() -> None:
    df = load_table(CHUNK_SUMMARY_PATH)
    print_section("Chunk Corpus")
    if df is None or df.empty:
        print(f"Missing or empty chunk summary: {CHUNK_SUMMARY_PATH}")
        return

    print(f"Rows: {len(df)}")
    print(f"Companies: {', '.join(sorted(df['company'].unique()))}")
    print(f"Fiscal years: {int(df['filing_year'].min())} -> {int(df['filing_year'].max())}")
    print(f"Sections sampled: {', '.join(sorted(df['section_name'].astype(str).unique())[:10])}")
    print("\nChunk counts by company/year:")
    counts = df.groupby(["company", "filing_year"]).size().reset_index(name="chunks")
    print(counts.to_string(index=False))


def summarize_structured_facts() -> None:
    df = load_sqlite_table(STRUCTURED_DB_PATH, "financial_facts")
    print_section("Structured Facts")
    if df is None or df.empty:
        print(f"Missing or empty structured facts table: {STRUCTURED_DB_PATH}")
        return

    print(f"Rows: {len(df)}")
    print(f"Companies: {', '.join(sorted(df['company'].unique()))}")
    print(f"Fiscal years: {int(df['fiscal_year'].min())} -> {int(df['fiscal_year'].max())}")
    cols = [
        "company",
        "fiscal_year",
        "total_revenue_musd",
        "net_income_musd",
        "total_assets_musd",
        "total_liabilities_musd",
        "cash_flow_from_operating_activities_musd",
    ]
    available_cols = [column for column in cols if column in df.columns]
    print("\nLatest available rows:")
    print(df[available_cols].tail(6).to_string(index=False))


def inspect_query() -> None:
    query = input("\nEnter a question to inspect inference (or press Enter to skip): ").strip()
    if not query:
        return

    plan = plan_query(query)
    retriever = RetrievalAdapter()
    chunks = retriever.search(
        plan.retrieval_query,
        top_k=5,
        company_filter=plan.companies or None,
        year_filter=plan.years or None,
    )

    print_section("Query Inference")
    print(f"Original query: {plan.query}")
    print(f"Detected companies: {plan.companies or 'none'}")
    print(f"Detected years: {plan.years or 'none'}")
    print(f"Detected metric: {plan.metric or 'none'}")
    print(f"Mode: {plan.mode}")
    print(f"Snapshot requested: {plan.snapshot_requested}")
    print(f"Assumption note: {plan.assumption_note or 'none'}")
    print(f"Retrieval query: {plan.retrieval_query}")

    print_section("Top Retrieved Chunks")
    if not chunks:
        print("No chunks matched the query filters.")
    else:
        for chunk in chunks:
            snippet = chunk.text[:500].replace("\n", " ")
            print(f"- {chunk.company} FY{chunk.filing_year} | {chunk.section_name} | score={chunk.score:.3f}")
            print(f"  {snippet}\n")


def main() -> None:
    summarize_ingest_manifest()
    summarize_chunk_corpus()
    summarize_structured_facts()
    inspect_query()


if __name__ == "__main__":
    main()
