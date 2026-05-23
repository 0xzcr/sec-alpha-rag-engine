from pathlib import Path


APP_NAME = "Financial RAG Chatbot"
WELCOME_MESSAGE = (
    "Ask a question about Microsoft, Tesla, or Apple financial filings. "
    "Type 'help' to see example prompts or 'exit' to quit."
)
EXAMPLE_PROMPTS = [
    "What was Microsoft's revenue in 2025?",
    "How did Tesla's net income change year over year?",
    "What risks are discussed in Apple's 10-K?",
    "Compare operating cash flow across the three companies.",
]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
