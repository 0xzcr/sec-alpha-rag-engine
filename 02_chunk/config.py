from pathlib import Path

RAW_MANIFEST_PATH = Path("data") / "raw" / "edgar" / "ingest_manifest.csv"
RAW_FILINGS_ROOT = Path("data") / "raw" / "edgar"
CHUNK_OUTPUT_ROOT = Path("data") / "processed" / "chunks"

TARGET_CHUNK_WORDS = 350
CHUNK_OVERLAP_WORDS = 50
MIN_CHUNK_WORDS = 80

SECTION_PATTERNS = [
    "item 1.",
    "item 1a.",
    "item 1b.",
    "item 2.",
    "item 3.",
    "item 7.",
    "item 7a.",
    "item 8.",
]
