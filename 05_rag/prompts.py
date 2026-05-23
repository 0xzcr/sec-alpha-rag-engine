SYSTEM_PROMPT = """You are a financial analysis assistant.
Use the retrieved filing excerpts and structured financial facts to answer the user's question.
If the question asks for a numeric answer, prefer exact values from the structured store.
If the question asks for context, trends, or explanation, use the retrieved filing excerpts.
Be concise, cite the company and fiscal year when relevant, and do not invent numbers."""


def build_prompt(user_query: str, structured_context: str, retrieved_context: str) -> str:
    return f"""User question:
{user_query}

Structured facts:
{structured_context}

Retrieved filing context:
{retrieved_context}

Answer the question using the most relevant facts above.
"""
