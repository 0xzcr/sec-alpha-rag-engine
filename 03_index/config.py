from pathlib import Path


CHUNK_SUMMARY_PATH = Path("data") / "processed" / "chunks" / "chunk_summary.jsonl"
INDEX_OUTPUT_ROOT = Path("data") / "index"
INDEX_ARTIFACT_PATH = INDEX_OUTPUT_ROOT / "tfidf_index.joblib"
INDEX_METADATA_PATH = INDEX_OUTPUT_ROOT / "chunk_metadata.jsonl"
INDEX_VOCAB_PATH = INDEX_OUTPUT_ROOT / "vectorizer_vocab.json"

MIN_DF = 1
NGRAM_RANGE = (1, 2)
MAX_FEATURES = 5000
