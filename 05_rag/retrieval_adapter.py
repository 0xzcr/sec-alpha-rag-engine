from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from dataclasses import dataclass
import sys
from typing import Any

import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

MODULE_DIR = Path(__file__).resolve().parent


def _load_config():
    spec = spec_from_file_location("_rag_config", MODULE_DIR / "config.py")
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load 05_rag/config.py")
    module = module_from_spec(spec)
    sys.modules["_rag_config"] = module
    spec.loader.exec_module(module)
    return module


INDEX_ARTIFACT_PATH = _load_config().INDEX_ARTIFACT_PATH


@dataclass
class RetrievedChunk:
    chunk_id: str
    score: float
    company: str
    ticker: str
    filing_year: int
    section_name: str
    text: str


class RetrievalAdapter:
    def __init__(self, artifact_path: Any = INDEX_ARTIFACT_PATH) -> None:
        artifact = joblib.load(artifact_path)
        self.vectorizer = artifact["vectorizer"]
        self.matrix = artifact["matrix"]
        self.metadata = artifact["metadata"]

    def search(
        self,
        query: str,
        top_k: int = 4,
        company_filter: list[str] | None = None,
        year_filter: list[int] | None = None,
    ) -> list[RetrievedChunk]:
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        if scores.size == 0:
            return []

        top_indices = np.argsort(scores)[::-1][:top_k]
        results: list[RetrievedChunk] = []
        for idx in top_indices:
            row = self.metadata.iloc[int(idx)]
            if company_filter and str(row["company"]) not in company_filter:
                continue
            if year_filter and int(row["filing_year"]) not in year_filter:
                continue
            results.append(
                RetrievedChunk(
                    chunk_id=str(row["chunk_id"]),
                    score=float(scores[idx]),
                    company=str(row["company"]),
                    ticker=str(row["ticker"]),
                    filing_year=int(row["filing_year"]),
                    section_name=str(row["section_name"]),
                    text=str(row["text"]),
                )
            )
        return results
