from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from config import (
    CHUNK_SUMMARY_PATH,
    INDEX_ARTIFACT_PATH,
    INDEX_METADATA_PATH,
    INDEX_OUTPUT_ROOT,
    INDEX_VOCAB_PATH,
    MAX_FEATURES,
    MIN_DF,
    NGRAM_RANGE,
)


@dataclass
class BuiltIndex:
    vectorizer: TfidfVectorizer
    matrix: Any
    metadata: pd.DataFrame


def load_chunks() -> pd.DataFrame:
    if not CHUNK_SUMMARY_PATH.exists():
        raise FileNotFoundError(
            f"Chunk summary not found at {CHUNK_SUMMARY_PATH}. Run 02_chunk first."
        )

    rows = []
    with CHUNK_SUMMARY_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    chunks = pd.DataFrame(rows)
    if "text" not in chunks.columns:
        raise ValueError("Chunk summary is missing the text column.")
    chunks = chunks.fillna("")
    return chunks


def build_tfidf_index(chunks: pd.DataFrame) -> BuiltIndex:
    vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True,
        ngram_range=NGRAM_RANGE,
        min_df=MIN_DF,
        max_features=MAX_FEATURES,
    )
    matrix = vectorizer.fit_transform(chunks["text"].astype(str).tolist())
    return BuiltIndex(vectorizer=vectorizer, matrix=matrix, metadata=chunks.copy())


def save_index(index: BuiltIndex) -> None:
    INDEX_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    vocabulary = {
        token: int(position) for token, position in index.vectorizer.vocabulary_.items()
    }
    joblib.dump(
        {
            "vectorizer": index.vectorizer,
            "matrix": index.matrix,
            "metadata": index.metadata,
        },
        INDEX_ARTIFACT_PATH,
    )
    with INDEX_METADATA_PATH.open("w", encoding="utf-8") as handle:
        for row in index.metadata.to_dict(orient="records"):
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    INDEX_VOCAB_PATH.write_text(
        json.dumps(vocabulary, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def main() -> None:
    chunks = load_chunks()
    index = build_tfidf_index(chunks)
    save_index(index)
    print(
        f"Indexing complete. Saved TF-IDF index for {len(chunks)} chunks to {INDEX_ARTIFACT_PATH}"
    )


if __name__ == "__main__":
    main()
