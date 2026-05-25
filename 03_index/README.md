# 03_index

This folder contains the indexing stage for the financial RAG pipeline.

## Purpose

- Load the chunk corpus produced by `02_chunk`
- Build a retrieval index from the chunk text
- Persist the vectorizer, matrix, and metadata for fast lookup
- Expose a lightweight retriever for later RAG stages

## Files

- `config.py` - index paths and vectorizer settings
- `index_sec_chunks.py` - builds and saves the TF-IDF index
- `retriever.py` - query helper for cosine-similarity retrieval

## Output Layout

```txt
data/index/
  tfidf_index.joblib
  chunk_metadata.jsonl
  vectorizer_vocab.json
```

## Run

```bash
python3 03_index/index_sec_chunks.py
```

## Design Notes

- This stage uses TF-IDF as a simple, reliable retrieval baseline.
- The retriever ranks chunks by cosine similarity between the query and chunk vectors.
- Later, this stage can be swapped to embeddings or a vector database without changing the pipeline shape.
