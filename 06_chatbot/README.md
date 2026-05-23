# 06_chatbot

This folder contains the user-facing chatbot stage for the financial RAG pipeline.

## Purpose

- Wrap the RAG engine in a simple interactive CLI
- Provide a friendly entrypoint for end users
- Keep the final layer lightweight and easy to run locally

## Files

- `config.py` - app name, help text, and example prompts
- `chatbot.py` - interactive CLI that calls the RAG engine

## Run

```bash
python3 06_chatbot/chatbot.py
```

## Supported Commands

- Ask a financial question directly
- Type `help` for example prompts
- Type `exit` or `quit` to leave the session

## Design Notes

- This stage is intentionally thin so the RAG logic stays centralized in `05_rag`.
- The CLI can be swapped for Flask, FastAPI, or a web frontend later without changing the earlier pipeline stages.
