# SEC Alpha RAG Engine Documentation

## Why This Was Built

This project was built to convert raw SEC 10-K filings into a grounded financial QA system that can answer open-ended questions about Apple, Microsoft, and Tesla. The objective was to move beyond one-off table extraction and implement a full retrieval-augmented workflow that supports both exact financial facts and narrative filing analysis.

The system is intentionally decomposed into stages so that ingestion, chunking, indexing, structured storage, retrieval, and generation can be evolved independently.

## How It Works

The pipeline follows this execution model:

1. Ingest SEC filing metadata and source documents.
2. Normalize filings into structured and raw artifacts.
3. Split filings into retrieval-ready chunks.
4. Build a sparse search index over the chunk corpus.
5. Persist exact financial metrics in a structured store.
6. Plan the query and retrieve the relevant evidence.
7. Synthesize the final answer with a local MLX model.

This creates a hybrid system:

- structured data for exact values
- retrieval for context and explanation
- local generation for final response synthesis

## Architecture

### 1. Ingest

Purpose: retrieve SEC submission metadata and raw filing documents.

Relevant files:

- [`01_ingest/config.py`](01_ingest/config.py)
- [`01_ingest/sec_client.py`](01_ingest/sec_client.py)
- [`01_ingest/ingest_sec_filings.py`](01_ingest/ingest_sec_filings.py)

Responsibilities:

- fetch filing metadata from SEC endpoints
- download 10-K text from EDGAR archives
- persist raw filings and manifests for downstream stages

### 2. Chunk

Purpose: convert raw filings into section-aware retrieval units.

Relevant files:

- [`02_chunk/config.py`](02_chunk/config.py)
- [`02_chunk/chunk_sec_filings.py`](02_chunk/chunk_sec_filings.py)

Responsibilities:

- normalize filing text
- detect SEC section markers
- build overlapping chunks to preserve local context
- emit chunk summaries for indexing

### 3. Index

Purpose: create a retrieval index over the chunk corpus.

Relevant files:

- [`03_index/config.py`](03_index/config.py)
- [`03_index/index_sec_chunks.py`](03_index/index_sec_chunks.py)
- [`03_index/retriever.py`](03_index/retriever.py)

Responsibilities:

- load the chunk corpus
- construct a TF-IDF vector space model
- persist index artifacts and vocabulary metadata
- provide cosine-similarity retrieval

### 4. Structured Store

Purpose: store exact financial facts in a queryable local database.

Relevant files:

- [`04_structured_store/config.py`](04_structured_store/config.py)
- [`04_structured_store/build_structured_store.py`](04_structured_store/build_structured_store.py)
- [`04_structured_store/store.py`](04_structured_store/store.py)

Responsibilities:

- consolidate SEC-derived company facts
- compute YoY deltas and derived ratios
- store exact facts in SQLite and JSONL artifacts
- expose lookup utilities for deterministic queries

### 5. RAG

Purpose: orchestrate retrieval and structured lookup into a single query context.

Relevant files:

- [`05_rag/config.py`](05_rag/config.py)
- [`05_rag/query_planner.py`](05_rag/query_planner.py)
- [`05_rag/retrieval_adapter.py`](05_rag/retrieval_adapter.py)
- [`05_rag/structured_store_adapter.py`](05_rag/structured_store_adapter.py)
- [`05_rag/prompts.py`](05_rag/prompts.py)
- [`05_rag/rag_engine.py`](05_rag/rag_engine.py)

Responsibilities:

- extract company, year, and metric signals from free-form questions
- route numeric questions to the structured store
- route narrative questions to filing retrieval
- assemble prompt-ready context for the generator

### 6. Chatbot

Purpose: provide the terminal-facing interaction layer.

Relevant files:

- [`06_chatbot/config.py`](06_chatbot/config.py)
- [`06_chatbot/chatbot.py`](06_chatbot/chatbot.py)

Responsibilities:

- accept user input in a REPL-style loop
- invoke the RAG engine
- print answers and supporting context in the terminal

### 7. Generation

Purpose: perform local answer generation with MLX on Apple Silicon.

Relevant files:

- [`generation/config.py`](generation/config.py)
- [`generation/prompts.py`](generation/prompts.py)
- [`generation/mlx_client.py`](generation/mlx_client.py)
- [`generation/app.py`](generation/app.py)

Responsibilities:

- validate upstream artifacts
- load the local MLX model
- translate RAG context into chat messages
- generate the final answer locally

### 8. Launcher

Purpose: bootstrap the whole pipeline from one shell entrypoint.

Relevant file:

- [`execute.sh`](execute.sh)

Responsibilities:

- run missing upstream stages when needed
- validate the SEC user-agent environment variable
- launch the interactive generation loop

## Problems Faced And Fixes

### SEC 4xx Errors

Problem:

- EDGAR requests intermittently failed with 4xx responses during parsing.

Fix:

- used declared SEC user-agent headers
- switched to SEC JSON endpoints where possible
- added throttling and retry handling for transient failures

### Cross-Stage Import Collisions

Problem:

- numbered stage folders contained duplicate module names such as `config.py`
- Python occasionally resolved imports from the wrong stage

Fix:

- loaded `05_rag` modules explicitly by file path
- avoided ambiguous bare imports in cross-stage orchestration code

### Missing Artifacts

Problem:

- generation failed when the index artifact or structured store did not exist

Fix:

- added prerequisite checks in the generation layer
- made `execute.sh` build missing stages before launching the chatbot

### JSON Serialization Failure

Problem:

- `numpy.int64` values in the TF-IDF vocabulary caused `json.dumps` failures

Fix:

- coerced vocabulary offsets to native Python `int` before serialization

### MLX API Version Mismatch

Problem:

- the installed `mlx-lm` release did not accept the older `temp` parameter path

Fix:

- switched to `make_sampler(...)`
- passed the sampler into `generate(...)`

### Weak Free-Form Question Handling

Problem:

- the initial bot behaved like a pre-recorded FAQ

Fix:

- added query planning for company, year, and metric detection
- filtered retrieval by company/year when available
- enabled open-ended 10-K question answering

## Current Result

The final system is a stage-based SEC financial RAG pipeline that can:

- ingest filings
- chunk them
- index them
- persist exact facts
- retrieve grounded evidence
- generate local answers with MLX

The main entrypoint is [`execute.sh`](execute.sh), which launches the full stack from the repository root.

## Problems Solved

This architecture addresses several common failure modes in modern RAG systems:

- **Long-context degradation**: 10-K filings are segmented into section-aware chunks so the model never has to reason over an entire filing monolithically.
- **Numeric hallucination risk**: exact financial values are sourced from a structured facts layer instead of being inferred from generated text.
- **Query ambiguity**: the query planner extracts company, year, and metric signals from free-form language before retrieval and generation.
- **Cross-company retrieval drift**: retrieval can be constrained by issuer and fiscal year, reducing context contamination across Apple, Microsoft, and Tesla.
- **EDGAR ingestion brittleness**: the ingest layer uses SEC-compliant request headers, throttling, retries, and archive-backed document access instead of fragile scraping.
- **Reproducibility gaps**: every stage persists artifacts to disk, including raw filings, chunk summaries, retrieval indexes, and structured tables.
- **External API dependence**: the generation layer runs locally on MLX, so the pipeline does not require a hosted LLM for the final synthesis step.
