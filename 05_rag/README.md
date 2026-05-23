# 05_rag

This folder contains the retrieval-augmented generation orchestration stage.

## Purpose

- Route questions to either structured data lookup or chunk retrieval
- Build prompt-ready context from both the vector index and the structured store
- Provide the final orchestration layer for the chatbot

## Files

- `config.py` - shared RAG paths and query-routing keywords
- `retrieval_adapter.py` - loads the saved chunk index and performs similarity search
- `structured_store_adapter.py` - loads the SQLite facts store for exact answers
- `prompts.py` - prompt templates for the generation layer
- `rag_engine.py` - main RAG orchestration and CLI demo

## Inputs

- `data/index/tfidf_index.joblib`
- `data/structured_store/financial_facts.sqlite`

## Run

```bash
python3 05_rag/rag_engine.py
```

## Design Notes

- Numeric questions are routed to the structured store first.
- Narrative and explanatory questions are grounded through retrieval.
- The generation hook is intentionally lightweight so it can later be swapped to an API-based LLM without changing the pipeline structure.
