# Financial Chatbot Documentation

## Overview

This repository now uses the SEC-backed RAG pipeline as the primary chatbot path. The older standalone demo entrypoint is retained only for compatibility and simply forwards into the MLX-powered generation app.

## Behavior

- Launch the chatbot with `./execute.sh`
- Choose the run or rebuild mode from the launcher menu
- Ask free-form questions about Apple, Microsoft, or Tesla 10-K filings

## What It Uses

- SEC ingestion artifacts
- section-aware filing chunks
- sparse retrieval over the chunk corpus
- structured SEC facts in SQLite
- local MLX generation

## Notes

- The legacy standalone demo is no longer the primary interface.
- The current chatbot is designed to answer open-ended filing questions rather than a fixed list of prompts.
