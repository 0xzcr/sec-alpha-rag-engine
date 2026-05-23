from config import SYSTEM_PROMPT


def build_messages(query: str, structured_context: str, retrieved_context: str) -> list[dict[str, str]]:
    user_message = f"""Question:
{query}

Structured facts:
{structured_context or "No structured facts were selected for this question."}

Retrieved filing context:
{retrieved_context or "No retrieval context was selected for this question."}

Instructions:
- Answer the user's question directly and naturally.
- If the question is about a company, year, or financial metric, use the structured facts first.
- If the question asks about risks, strategy, business description, outlook, or other narrative content, use the retrieved filing context.
- If the user phrase is ambiguous (for example, "finances" or "earnings"), infer the most likely financial metric and state the assumption briefly.
- Do not say the question is unsupported if the context clearly contains the answer.
- If multiple companies or years are relevant, compare them concisely.
- Keep the answer grounded in Apple, Microsoft, and Tesla 10-K content only.
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
