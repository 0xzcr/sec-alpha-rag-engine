from __future__ import annotations

from pathlib import Path
import sys

from config import (
    DEFAULT_WELCOME,
    EXAMPLE_QUESTIONS,
    INDEX_ARTIFACT_PATH,
    RAG_STAGE_PATH,
    STRUCTURED_STORE_PATH,
)
from mlx_client import MlxTextGenerator
from prompts import build_messages

if str(RAG_STAGE_PATH) not in sys.path:
    sys.path.insert(0, str(RAG_STAGE_PATH))

from rag_engine import FinancialRAGEngine  # noqa: E402


def validate_prerequisites() -> None:
    missing = []
    if not INDEX_ARTIFACT_PATH.exists():
        missing.append(f"Missing retrieval index: {INDEX_ARTIFACT_PATH}")
    if not STRUCTURED_STORE_PATH.exists():
        missing.append(f"Missing structured store: {STRUCTURED_STORE_PATH}")

    if missing:
        message_lines = [
            "The generation layer cannot start because upstream artifacts are missing.",
            *missing,
            "",
            "Run the earlier stages first:",
            "1. 01_ingest",
            "2. 02_chunk",
            "3. 03_index",
            "4. 04_structured_store",
            "",
            "Then rerun: python3 generation/app.py",
        ]
        raise FileNotFoundError("\n".join(message_lines))


class GenerationApp:
    def __init__(self) -> None:
        self.rag_engine = FinancialRAGEngine()
        self.generator = MlxTextGenerator()

    def answer(self, query: str) -> str:
        rag_response = self.rag_engine.generate_answer(query)
        messages = build_messages(
            query=query,
            structured_context=rag_response.structured_context,
            retrieved_context=rag_response.retrieved_context,
        )
        return self.generator.generate(messages)


def print_help() -> None:
    print("\nYou can ask anything about the Apple, Microsoft, or Tesla 10-Ks.")
    print("Example prompts:")
    for prompt in EXAMPLE_QUESTIONS:
        print(f"- {prompt}")
    print()


def main() -> None:
    validate_prerequisites()
    app = GenerationApp()
    print(DEFAULT_WELCOME)
    print()

    while True:
        query = input("You: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Assistant: Goodbye.")
            break
        if query.lower() == "help":
            print_help()
            continue

        try:
            answer = app.answer(query)
            print(f"Assistant: {answer}\n")
        except Exception as error:  # noqa: BLE001
            print(f"Assistant: Generation failed: {error}\n")


if __name__ == "__main__":
    main()
