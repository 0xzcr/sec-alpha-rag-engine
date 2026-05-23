# 02_chunk

This folder contains the chunking stage for the financial RAG pipeline.

## Purpose

- Read the raw filing manifest created by `01_ingest`
- Clean and normalize the filing text
- Split filings into section-aware chunks suitable for retrieval
- Write chunk artifacts for the indexing stage

## Files

- `config.py` - chunking paths and parameters
- `chunk_sec_filings.py` - transforms raw filings into chunk files

## Output Layout

```txt
data/processed/chunks/
  msft/
    msft_chunks.jsonl
    msft_chunks.csv
  tsla/
  aapl/
  chunk_summary.csv
```

## Run

```bash
python3 02_chunk/chunk_sec_filings.py
```

## Design Notes

- Chunking is section-aware when common SEC item markers are present.
- If no section markers are found, the whole document is treated as a fallback source.
- Chunks are built with a target word window and overlap to preserve context for retrieval.
