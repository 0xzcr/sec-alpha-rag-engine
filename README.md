# SEC Alpha RAG Engine Documentation

## Why This Was Built

This project was built to turn raw SEC 10-K filings into a usable financial analysis system that can answer questions about Apple, Microsoft, and Tesla in a grounded way. The goal was to move from static CSV extraction into a full retrieval-augmented workflow that can support both exact financial facts and narrative filing questions.

The design was intentionally split into stages so each part of the pipeline has a clear responsibility and can be improved independently.

## How It Works

The pipeline follows a simple flow:

1. Download and archive SEC filings.
2. Split the filings into retrieval-friendly chunks.
3. Build a search index over the chunked text.
4. Store structured financial facts for exact lookups.
5. Plan the user query and retrieve the right evidence.
6. Use MLX to generate the final answer locally.

The result is a hybrid system:

- structured data for exact numbers
- retrieval for filing context
- local generation for the final response

## Architecture

### 1. Ingest

Purpose: fetch SEC submission metadata and raw filing documents.

Relevant files:

- [`01_ingest/config.py`](01_ingest/config.py)
- [`01_ingest/sec_client.py`](01_ingest/sec_client.py)
- [`01_ingest/ingest_sec_filings.py`](01_ingest/ingest_sec_filings.py)

What it does:

- pulls filing metadata from SEC endpoints
- downloads 10-K filing text
- saves raw filings and a manifest for later stages

### 2. Chunk

Purpose: convert raw filings into section-aware retrieval chunks.

Relevant files:

- [`02_chunk/config.py`](02_chunk/config.py)
- [`02_chunk/chunk_sec_filings.py`](02_chunk/chunk_sec_filings.py)

What it does:

- cleans filing text
- detects SEC section markers
- splits filings into overlapping chunks
- writes a chunk summary for indexing

### 3. Index

Purpose: build a retriever over the chunk corpus.

Relevant files:

- [`03_index/config.py`](03_index/config.py)
- [`03_index/index_sec_chunks.py`](03_index/index_sec_chunks.py)
- [`03_index/retriever.py`](03_index/retriever.py)

What it does:

- loads the chunk summary
- creates a TF-IDF matrix
- stores the index artifact and vocabulary
- exposes cosine-similarity retrieval

### 4. Structured Store

Purpose: store exact financial figures in a queryable table.

Relevant files:

- [`04_structured_store/config.py`](04_structured_store/config.py)
- [`04_structured_store/build_structured_store.py`](04_structured_store/build_structured_store.py)
- [`04_structured_store/store.py`](04_structured_store/store.py)

What it does:

- consolidates the company CSV files
- calculates YoY and ratio-based derived metrics
- writes CSV and SQLite outputs
- exposes exact lookup methods for later stages

### 5. RAG

Purpose: combine retrieval and structured data into a query-ready context layer.

Relevant files:

- [`05_rag/config.py`](05_rag/config.py)
- [`05_rag/query_planner.py`](05_rag/query_planner.py)
- [`05_rag/retrieval_adapter.py`](05_rag/retrieval_adapter.py)
- [`05_rag/structured_store_adapter.py`](05_rag/structured_store_adapter.py)
- [`05_rag/prompts.py`](05_rag/prompts.py)
- [`05_rag/rag_engine.py`](05_rag/rag_engine.py)

What it does:

- detects company, year, and likely metric from free-form questions
- routes numeric questions toward structured facts
- routes narrative questions toward filing chunks
- prepares prompt-ready context for the generator

### 6. Chatbot

Purpose: provide the interactive terminal interface.

Relevant files:

- [`06_chatbot/config.py`](06_chatbot/config.py)
- [`06_chatbot/chatbot.py`](06_chatbot/chatbot.py)

What it does:

- accepts user questions in the terminal
- calls the RAG layer behind the scenes
- prints responses in a simple interactive loop

### 7. Generation

Purpose: use MLX for local answer generation.

Relevant files:

- [`generation/config.py`](generation/config.py)
- [`generation/prompts.py`](generation/prompts.py)
- [`generation/mlx_client.py`](generation/mlx_client.py)
- [`generation/app.py`](generation/app.py)

What it does:

- checks that the upstream artifacts exist
- loads the local MLX model
- converts the RAG context into a chat prompt
- generates the final answer on the MacBook

### 8. Project Launcher

Purpose: run the entire pipeline from one command.

Relevant file:

- [`execute.sh`](execute.sh)

What it does:

- runs the missing upstream stages if needed
- validates the required SEC environment variable
- launches the interactive generation loop

## Problems Faced And Fixes

### SEC 4xx Errors

Problem:

- EDGAR requests failed with 4xx errors during parsing.

Fix:

- used declared SEC user-agent headers
- relied on SEC JSON endpoints instead of brittle scraping
- added throttling and retry logic for transient failures

### Numbered Folder Import Collisions

Problem:

- folders like `05_rag` and `generation` both had a `config.py`
- Python sometimes imported the wrong one

Fix:

- loaded local modules explicitly by file path inside `05_rag`
- avoided bare `from config import ...` in cross-stage code

### Missing Pipeline Artifacts

Problem:

- generation failed when `data/index/tfidf_index.joblib` or the SQLite store did not exist

Fix:

- added a prerequisite check in `generation/app.py`
- made `execute.sh` build missing stages before launching the chatbot

### JSON Serialization Error In Indexing

Problem:

- `numpy.int64` values in the TF-IDF vocabulary could not be serialized with `json.dumps`

Fix:

- cast vocabulary values to native Python `int` before writing the JSON file

### MLX API Mismatch

Problem:

- the installed `mlx-lm` version did not accept `temp` directly in `generate()`

Fix:

- switched to `make_sampler(...)` and passed the sampler into `generate()`
- updated the call to use the installed API shape

### Weak Free-Form Question Handling

Problem:

- the system originally behaved like a pre-recorded FAQ

Fix:

- added query planning for company, year, and metric detection
- enabled retrieval with company/year filters
- made the system respond to open-ended 10-K questions instead of only canned prompts

## Current Result

The project is now organized as a stage-based SEC financial RAG pipeline that can:

- ingest filings
- chunk them
- index them
- store exact facts
- retrieve relevant evidence
- generate answers locally with MLX

The main entrypoint is [`execute.sh`](execute.sh), which launches the full pipeline from one command.
