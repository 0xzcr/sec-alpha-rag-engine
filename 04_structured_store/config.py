from pathlib import Path


STRUCTURED_INPUT_FILES = [
    Path("microsoft_10k_financials_2023_2025.csv"),
    Path("tesla_10k_financials_2023_2025.csv"),
    Path("apple_10k_financials_2023_2025.csv"),
]

STRUCTURED_OUTPUT_ROOT = Path("data") / "structured_store"
CONSOLIDATED_TABLE_PATH = STRUCTURED_OUTPUT_ROOT / "financial_facts.csv"
SUMMARY_TABLE_PATH = STRUCTURED_OUTPUT_ROOT / "financial_summary.csv"
SQLITE_DB_PATH = STRUCTURED_OUTPUT_ROOT / "financial_facts.sqlite"

METRIC_COLUMNS = [
    "total_revenue_musd",
    "net_income_musd",
    "total_assets_musd",
    "total_liabilities_musd",
    "cash_flow_from_operating_activities_musd",
]
