#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

run_stage() {
  local label="$1"
  local command="$2"
  echo
  echo "==> ${label}"
  eval "$command"
}

ensure_artifacts() {
  local missing=0

  if [[ ! -f "data/index/tfidf_index.joblib" ]]; then
    missing=1
  fi

  if [[ ! -f "data/structured_store/financial_facts.sqlite" ]]; then
    missing=1
  fi

  if [[ "$missing" -eq 0 ]]; then
    return 1
  fi

  return 0
}

echo "Starting SEC alpha RAG pipeline..."

if ensure_artifacts; then
  echo "Upstream artifacts missing. Building pipeline stages first."

  if [[ -z "${SEC_USER_AGENT:-}" ]]; then
    echo "SEC_USER_AGENT is not set."
    echo "Set it first, for example:"
    echo 'export SEC_USER_AGENT="Your Name your.email@example.com"'
    exit 1
  fi

  run_stage "01_ingest" "python3 01_ingest/ingest_sec_filings.py"
  run_stage "02_chunk" "python3 02_chunk/chunk_sec_filings.py"
  run_stage "03_index" "python3 03_index/index_sec_chunks.py"
  run_stage "04_structured_store" "python3 04_structured_store/build_structured_store.py"
else
  echo "Found existing retrieval and structured-store artifacts."
fi

echo
echo "Launching interactive generation layer..."
exec python3 generation/app.py
