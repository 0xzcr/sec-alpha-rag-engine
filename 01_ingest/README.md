# 01_ingest

This folder contains the SEC EDGAR ingestion stage for the financial RAG pipeline.

## Purpose

- Fetch company submission metadata from `data.sec.gov`
- Select the 10-K filings for the requested fiscal years
- Download the filing HTML/text from SEC archives
- Save a local raw corpus and ingestion manifest for later stages

## Files

- `config.py` - company list, year range, and output paths
- `sec_client.py` - SEC HTTP client with declared user-agent, throttling, and retries
- `ingest_sec_filings.py` - stage runner that builds the raw filing archive

## Output Layout

```txt
data/raw/edgar/
  msft/
    submissions.json
    companyfacts.json
    2023/
      <primary_document>.htm
      metadata.json
  tsla/
  aapl/
  ingest_manifest.jsonl
```

## Run

```bash
export SEC_USER_AGENT="Your Name your.email@example.com"
python3 01_ingest/ingest_sec_filings.py
```

## Design Notes

- The client avoids scraping search pages and uses the SEC JSON endpoints instead.
- Requests are throttled and retried only for transient HTTP failures.
- A manifest is written so later stages can reliably reference the exact raw filing files.
