from __future__ import annotations

from config import APP_NAME, EXAMPLE_PROMPTS, WELCOME_MESSAGE

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAG_DIR = PROJECT_ROOT / "05_rag"
if str(RAG_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_DIR))

from rag_engine import FinancialRAGEngine  # noqa: E402


def format_response(query: str, response) -> str:
    lines = [
        f"Question: {query}",
        f"Mode: {response.query_type}",
        f"Answer: {response.answer}",
    ]
    if response.structured_context:
        lines.append("\nStructured facts:")
        lines.append(response.structured_context)
    if response.retrieved_context:
        lines.append("\nRetrieved context:")
        lines.append(response.retrieved_context)
    return "\n".join(lines)


def print_help() -> None:
    print("\nExample prompts:")
    for prompt in EXAMPLE_PROMPTS:
        print(f"- {prompt}")
    print()


def main() -> None:
    engine = FinancialRAGEngine()
    print(APP_NAME)
    print(WELCOME_MESSAGE)
    print()

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Chatbot: Goodbye.")
            break
        if user_input.lower() == "help":
            print_help()
            continue

        response = engine.generate_answer(user_input)
        print(f"Chatbot: {format_response(user_input, response)}\n")


if __name__ == "__main__":
    main()
