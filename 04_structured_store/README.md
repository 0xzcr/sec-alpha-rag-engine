# 04_structured_store

This folder contains the structured financial data layer for the pipeline.

## Purpose

- Consolidate the company-level financial CSVs from Task 1
- Add derived metrics such as YoY change, profit margin, and asset/liability ratio
- Store the cleaned data in CSV and SQLite formats for exact-number queries
- Provide a lightweight query API for downstream chatbot/RAG logic

## Files

- `config.py` - input files and output paths
- `build_structured_store.py` - creates the consolidated tables and SQLite database
- `store.py` - query helper for loading and filtering structured financial data

## Output Layout

```txt
data/structured_store/
  financial_facts.csv
  financial_summary.csv
  financial_facts.sqlite
```

## Run

```bash
python3 04_structured_store/build_structured_store.py
```

## Design Notes

- This is the “exact facts” layer of the pipeline, not a semantic retrieval layer.
- The SQLite table is useful for deterministic lookup, comparisons, and calculations.
- The derived fields are precomputed so later stages can answer trend questions efficiently.
