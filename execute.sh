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

ensure_sec_user_agent() {
  if [[ -z "${SEC_USER_AGENT:-}" ]]; then
    echo "SEC_USER_AGENT is not set."
    echo "Set it first, for example:"
    echo 'export SEC_USER_AGENT="Your Name your.email@example.com"'
    exit 1
  fi
}

ensure_artifacts() {
  [[ \
    -f "data/raw/edgar/ingest_manifest.jsonl" && \
    -f "data/processed/chunks/chunk_summary.jsonl" && \
    -f "data/index/tfidf_index.joblib" && \
    -f "data/structured_store/financial_facts.sqlite" && \
    -f "data/raw/edgar/companyfacts/aapl.json" && \
    -f "data/raw/edgar/companyfacts/msft.json" && \
    -f "data/raw/edgar/companyfacts/tsla.json" \
  ]]
}

rebuild_pipeline() {
  ensure_sec_user_agent

  run_stage "01_ingest" "python3 01_ingest/ingest_sec_filings.py"
  run_stage "02_chunk" "python3 02_chunk/chunk_sec_filings.py"
  run_stage "03_index" "python3 03_index/index_sec_chunks.py"
  run_stage "04_structured_store" "python3 04_structured_store/build_structured_store.py"
}

launch_generation() {
  echo
  echo "Launching interactive generation layer..."
  exec python3 generation/app.py
}

show_menu() {
  cat <<'EOF'
Select a mode:
  1) Rebuild pipeline and run RAG
  2) Run RAG with existing artifacts
  3) Inspect ingested data and inferred query plan (development only)
  4) Exit
EOF
}

main() {
  echo "SEC Alpha RAG Launcher"
  show_menu
  read -r choice

  case "$choice" in
    1)
      echo "Rebuilding pipeline..."
      rebuild_pipeline
      launch_generation
      ;;
    2)
      if ensure_artifacts; then
        echo "Found existing artifacts."
        launch_generation
      else
        echo "Required artifacts are missing."
        echo "Switching to rebuild mode."
        rebuild_pipeline
        launch_generation
      fi
      ;;
    3)
      echo "Launching inspection utility..."
      python3 inspect_rag.py
      ;;
    4)
      echo "Exiting."
      exit 0
      ;;
    *)
      echo "Invalid choice."
      exit 1
      ;;
  esac
}

main "$@"
