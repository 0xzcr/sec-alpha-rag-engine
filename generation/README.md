# generation

This folder is the final generation layer of the financial RAG pipeline.

## What this stage does

1. Takes a user question.
2. Calls the RAG layer to get structured facts and retrieved filing context.
3. Builds an instruction prompt for a local MLX model.
4. Uses `mlx-lm` to generate the final answer on your Mac.

## Folder layout

```txt
generation/
  config.py
  prompts.py
  mlx_client.py
  app.py
  README.md
```

## What you need to provide

- A Mac with Apple Silicon and Metal support
- `mlx-lm` installed in your Python environment
- The outputs from earlier stages:
  - `data/index/tfidf_index.joblib`
  - `data/structured_store/financial_facts.sqlite`
- An MLX-compatible model repo or local path
- Enough free disk space for the downloaded model

## Recommended model choice for an M1 Air 8 GB

- Start with a small 3B or 4B instruct model in 4-bit format
- Use the `MLX_MODEL_REPO` environment variable to override the default model

Example:

```bash
export MLX_MODEL_REPO="mlx-community/Qwen2.5-3B-Instruct-4bit"
```

## Install

```bash
pip install mlx-lm
```

If `mlx-lm` is already installed, just make sure you are running on your MacBook and not in a headless environment.

## Run

```bash
python3 generation/app.py
```

## Expected architecture

```txt
User question
   ↓
RAG context builder
   ↓
Prompt builder
   ↓
MLX model
   ↓
Final answer
```

## Notes

- Numeric questions should rely on the structured store.
- Explanation questions should rely on the retrieved filing text.
- If the model hallucinates, reduce the context size or switch to a stronger instruct model.
- This layer is intentionally separate from the earlier retrieval and storage stages so you can swap the model without touching ingestion or indexing.
