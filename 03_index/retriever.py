from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from config import INDEX_ARTIFACT_PATH


@dataclass
class RetrievalResult:
    chunk_id: str
    score: float
    company: str
    ticker: str
    filing_year: int
    section_name: str
    text: str


class TfidfRetriever:
    def __init__(self, artifact_path: Any = INDEX_ARTIFACT_PATH) -> None:
        artifact = joblib.load(artifact_path)
        self.vectorizer = artifact["vectorizer"]
        self.matrix = artifact["matrix"]
        self.metadata = artifact["metadata"]

    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        if scores.size == 0:
            return []

        top_indices = np.argsort(scores)[::-1][:top_k]
        results: list[RetrievalResult] = []
        for idx in top_indices:
            row = self.metadata.iloc[int(idx)]
            results.append(
                RetrievalResult(
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
