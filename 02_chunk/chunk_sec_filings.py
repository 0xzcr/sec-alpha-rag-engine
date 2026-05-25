from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html import unescape
from pathlib import Path

import pandas as pd
from config import (
    CHUNK_OUTPUT_ROOT,
    CHUNK_SUMMARY_PATH,
    CHUNK_OVERLAP_WORDS,
    MIN_CHUNK_WORDS,
    RAW_FILINGS_ROOT,
    RAW_MANIFEST_PATH,
    SECTION_PATTERNS,
    TARGET_CHUNK_WORDS,
)


@dataclass
class FilingChunk:
    chunk_id: str
    company: str
    ticker: str
    filing_year: int
    filing_date: str
    accession_number: str
    primary_document: str
    source_path: str
    section_name: str
    chunk_index: int
    text: str

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "company": self.company,
            "ticker": self.ticker,
            "filing_year": self.filing_year,
            "filing_date": self.filing_date,
            "accession_number": self.accession_number,
            "primary_document": self.primary_document,
            "source_path": self.source_path,
            "section_name": self.section_name,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "word_count": len(self.text.split()),
        }


def load_manifest() -> pd.DataFrame:
    if not RAW_MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Manifest not found at {RAW_MANIFEST_PATH}. Run 01_ingest first."
        )

    rows = []
    with RAW_MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    manifest = pd.DataFrame(rows)
    if manifest.empty:
        return manifest
    manifest["filing_year"] = manifest["filing_year"].astype(int)
    return manifest.sort_values(["company", "filing_year"]).reset_index(drop=True)


def read_filing_text(path: Path) -> str:
    raw_text = path.read_text(encoding="utf-8", errors="ignore")
    cleaned_text = unescape(raw_text)
    cleaned_text = re.sub(
        r"<script.*?>.*?</script>", " ", cleaned_text, flags=re.I | re.S
    )
    cleaned_text = re.sub(
        r"<style.*?>.*?</style>", " ", cleaned_text, flags=re.I | re.S
    )
    cleaned_text = re.sub(r"<[^>]+>", " ", cleaned_text)
    cleaned_text = re.sub(r"&nbsp;|&#160;", " ", cleaned_text, flags=re.I)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    return cleaned_text.strip()


def split_into_sections(text: str) -> list[tuple[str, str]]:
    normalized = text.lower()
    markers: list[tuple[int, str]] = []

    for pattern in SECTION_PATTERNS:
        match = re.search(rf"\b{re.escape(pattern)}", normalized)
        if match:
            markers.append((match.start(), pattern))

    markers.sort(key=lambda item: item[0])
    if not markers:
        return [("full_document", text)]

    sections: list[tuple[str, str]] = []
    for idx, (start_pos, pattern) in enumerate(markers):
        end_pos = markers[idx + 1][0] if idx + 1 < len(markers) else len(text)
        section_text = text[start_pos:end_pos].strip()
        if len(section_text.split()) >= MIN_CHUNK_WORDS:
            sections.append((pattern.replace(".", "").upper(), section_text))

    if not sections:
        return [("full_document", text)]
    return sections


def windowed_chunks(
    words: list[str], target_size: int, overlap: int
) -> list[list[str]]:
    if not words:
        return []

    chunks: list[list[str]] = []
    start = 0
    while start < len(words):
        end = min(start + target_size, len(words))
        chunk_words = words[start:end]
        if len(chunk_words) >= MIN_CHUNK_WORDS:
            chunks.append(chunk_words)
        if end >= len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


def build_chunks_for_filing(manifest_row: pd.Series) -> list[FilingChunk]:
    source_path = Path(manifest_row["local_path"])
    text = read_filing_text(source_path)
    sections = split_into_sections(text)

    filing_chunks: list[FilingChunk] = []
    chunk_counter = 0

    for section_name, section_text in sections:
        section_words = section_text.split()
        for chunk_words in windowed_chunks(
            section_words, TARGET_CHUNK_WORDS, CHUNK_OVERLAP_WORDS
        ):
            chunk_counter += 1
            chunk_text = " ".join(chunk_words)
            chunk_id = (
                f"{manifest_row['ticker'].lower()}-"
                f"{int(manifest_row['filing_year'])}-"
                f"{chunk_counter:03d}"
            )
            filing_chunks.append(
                FilingChunk(
                    chunk_id=chunk_id,
                    company=manifest_row["company"],
                    ticker=manifest_row["ticker"],
                    filing_year=int(manifest_row["filing_year"]),
                    filing_date=str(manifest_row["filing_date"]),
                    accession_number=str(manifest_row["accession_number"]),
                    primary_document=str(manifest_row["primary_document"]),
                    source_path=str(source_path),
                    section_name=section_name,
                    chunk_index=chunk_counter,
                    text=chunk_text,
                )
            )

    return filing_chunks


def write_chunk_outputs(rows: list[FilingChunk], company: str, ticker: str) -> None:
    company_root = CHUNK_OUTPUT_ROOT / ticker.lower()
    company_root.mkdir(parents=True, exist_ok=True)

    jsonl_path = company_root / f"{ticker.lower()}_chunks.jsonl"

    with jsonl_path.open("w", encoding="utf-8") as jsonl_file:
        for row in rows:
            jsonl_file.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")


def main() -> None:
    manifest = load_manifest()
    all_chunks: list[FilingChunk] = []

    for _, row in manifest.iterrows():
        all_chunks.extend(build_chunks_for_filing(row))

    if not all_chunks:
        raise RuntimeError(
            "No chunks were created. Check the ingest output and source filings."
        )

    grouped: dict[tuple[str, str], list[FilingChunk]] = {}
    for chunk in all_chunks:
        grouped.setdefault((chunk.company, chunk.ticker), []).append(chunk)

    for (company, ticker), chunks in grouped.items():
        write_chunk_outputs(chunks, company, ticker)

    CHUNK_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    summary_rows = [chunk.to_dict() for chunk in all_chunks]
    with CHUNK_SUMMARY_PATH.open("w", encoding="utf-8") as handle:
        for row in summary_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Chunking complete. Wrote {len(all_chunks)} chunks to {CHUNK_OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
