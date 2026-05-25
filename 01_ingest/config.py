from pathlib import Path

START_YEAR = 2018
END_YEAR = 2025

COMPANIES = [
    {
        "name": "Microsoft",
        "ticker": "MSFT",
        "cik": "0000789019",
    },
    {
        "name": "Tesla",
        "ticker": "TSLA",
        "cik": "0001318605",
    },
    {
        "name": "Apple",
        "ticker": "AAPL",
        "cik": "0000320193",
    },
]

RAW_DATA_DIR = Path("data") / "raw" / "edgar"
MANIFEST_PATH = RAW_DATA_DIR / "ingest_manifest.jsonl"
COMPANY_FACTS_DIR = RAW_DATA_DIR / "companyfacts"
