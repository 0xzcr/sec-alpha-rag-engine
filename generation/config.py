from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAG_STAGE_PATH = PROJECT_ROOT / "05_rag"
INDEX_ARTIFACT_PATH = PROJECT_ROOT / "data" / "index" / "tfidf_index.joblib"
STRUCTURED_STORE_PATH = PROJECT_ROOT / "data" / "structured_store" / "financial_facts.sqlite"

DEFAULT_MODEL_REPO = "mlx-community/Qwen2.5-3B-Instruct-4bit"
MODEL_REPO_ENV = "MLX_MODEL_REPO"

MAX_TOKENS = 512
TEMPERATURE = 0.2
TOP_P = 0.9

SYSTEM_PROMPT = (
    "You are a financial analysis assistant. Use only the supplied structured facts "
    "and retrieved filing excerpts. If the answer is numeric, prefer the structured "
    "store. If the question is explanatory, use the filing context. If the answer "
    "is not supported by the context, say so clearly."
)

DEFAULT_WELCOME = (
    "Financial Generation Layer ready. Ask a question, type 'help' for examples, "
    "or type 'exit' to quit."
)

EXAMPLE_QUESTIONS = [
    "What was Microsoft's revenue in 2025?",
    "How did Tesla's net income change year over year?",
    "What risks are discussed in Apple's 10-K?",
    "Compare operating cash flow across the three companies.",
]
