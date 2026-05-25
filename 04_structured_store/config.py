from pathlib import Path


SEC_COMPANY_FACTS_DIR = Path("data") / "raw" / "edgar" / "companyfacts"

STRUCTURED_OUTPUT_ROOT = Path("data") / "structured_store"
CONSOLIDATED_TABLE_PATH = STRUCTURED_OUTPUT_ROOT / "financial_facts.jsonl"
SUMMARY_TABLE_PATH = STRUCTURED_OUTPUT_ROOT / "financial_summary.json"
SQLITE_DB_PATH = STRUCTURED_OUTPUT_ROOT / "financial_facts.sqlite"

START_YEAR = 2018
END_YEAR = 2025

METRIC_COLUMNS = [
    "total_revenue_musd",
    "net_income_musd",
    "total_assets_musd",
    "total_liabilities_musd",
    "cash_flow_from_operating_activities_musd",
]

COMPANY_TICKERS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
}

CONCEPT_ALIASES = {
    "total_revenue_musd": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ],
    "net_income_musd": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],
    "total_assets_musd": [
        "Assets",
    ],
    "total_liabilities_musd": [
        "Liabilities",
    ],
    "cash_flow_from_operating_activities_musd": [
        "NetCashProvidedByUsedInOperatingActivities",
    ],
}
