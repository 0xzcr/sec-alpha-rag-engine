from pathlib import Path


INDEX_ARTIFACT_PATH = Path("data") / "index" / "tfidf_index.joblib"
STRUCTURED_STORE_PATH = Path("data") / "structured_store" / "financial_facts.sqlite"
STRUCTURED_TABLE_NAME = "financial_facts"

DEFAULT_TOP_K = 4
DEFAULT_NUMERIC_TOP_K = 3

NUMERIC_KEYWORDS = [
    "revenue",
    "income",
    "assets",
    "liabilities",
    "cash flow",
    "operating cash flow",
    "operating activities",
    "margin",
    "yoy",
    "year over year",
    "compare",
]
