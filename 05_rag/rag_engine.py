from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from dataclasses import dataclass
import sys
from typing import Literal

MODULE_DIR = Path(__file__).resolve().parent


def _load_module(module_name: str, filename: str):
    spec = spec_from_file_location(module_name, MODULE_DIR / filename)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {filename}")
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_config = _load_module("_rag_config", "config.py")
_prompts = _load_module("_rag_prompts", "prompts.py")
_query_planner = _load_module("_rag_query_planner", "query_planner.py")
_retrieval_adapter = _load_module("_rag_retrieval_adapter", "retrieval_adapter.py")
_structured_store_adapter = _load_module("_rag_structured_store_adapter", "structured_store_adapter.py")

DEFAULT_NUMERIC_TOP_K = _config.DEFAULT_NUMERIC_TOP_K
DEFAULT_TOP_K = _config.DEFAULT_TOP_K
NUMERIC_KEYWORDS = _config.NUMERIC_KEYWORDS
SYSTEM_PROMPT = _prompts.SYSTEM_PROMPT
build_prompt = _prompts.build_prompt
plan_query = _query_planner.plan_query
QueryPlan = _query_planner.QueryPlan
RetrievalAdapter = _retrieval_adapter.RetrievalAdapter
StructuredStoreAdapter = _structured_store_adapter.StructuredStoreAdapter


@dataclass
class RagResponse:
    query_type: Literal["numeric", "context"]
    answer: str
    structured_context: str
    retrieved_context: str


class FinancialRAGEngine:
    def __init__(self) -> None:
        self.retriever = RetrievalAdapter()
        self.store = StructuredStoreAdapter()

    def _format_structured_context(self, plan: QueryPlan) -> str:
        target_companies = plan.companies or ["Apple", "Microsoft", "Tesla"]
        lines: list[str] = []

        for company in target_companies:
            company_df = self.store.fetch_company(company)
            if company_df.empty:
                continue

            if plan.years:
                candidate_rows = [
                    self.store.fetch_company_year(company, year) for year in plan.years
                ]
                rows = [row for row in candidate_rows if row is not None]
            else:
                rows = [company_df.iloc[-1]]

            for row in rows:
                fiscal_year = int(row["fiscal_year"])
                if plan.metric and plan.metric in row:
                    value = row[plan.metric]
                    label = plan.metric.replace("_musd", "").replace("_", " ")
                    lines.append(f"{company} FY{fiscal_year}: {label} = {value}")
                else:
                    lines.append(
                        f"{company} FY{fiscal_year}: revenue={row['total_revenue_musd']}, "
                        f"net income={row['net_income_musd']}, assets={row['total_assets_musd']}, "
                        f"liabilities={row['total_liabilities_musd']}, operating cash flow="
                        f"{row['cash_flow_from_operating_activities_musd']}"
                    )

        if plan.assumption_note:
            lines.insert(0, plan.assumption_note)

        return "\n".join(lines)

    def _format_retrieved_context(self, plan: QueryPlan, top_k: int) -> str:
        chunks = self.retriever.search(
            plan.retrieval_query,
            top_k=top_k,
            company_filter=plan.companies or None,
            year_filter=plan.years or None,
        )
        if not chunks:
            return "No relevant filing chunks found."
        lines = []
        for chunk in chunks:
            snippet = chunk.text[:700].replace("\n", " ")
            lines.append(
                f"[{chunk.company} FY{chunk.filing_year} | {chunk.section_name} | score={chunk.score:.3f}] {snippet}"
            )
        return "\n".join(lines)

    def generate_answer(self, query: str) -> RagResponse:
        plan = plan_query(query)
        query_type: Literal["numeric", "context"] = "numeric" if plan.mode == "numeric" else "context"
        structured_context = self._format_structured_context(plan) if plan.mode in {"numeric", "mixed"} else ""
        retrieved_context = self._format_retrieved_context(
            plan,
            top_k=DEFAULT_NUMERIC_TOP_K if plan.mode == "numeric" else DEFAULT_TOP_K,
        )

        if plan.mode == "numeric":
            answer = (
                "This question is answered from the structured financial facts, with retrieval as supporting context."
            )
        else:
            answer = (
                "This question is answered from the retrieved 10-K context, grounded in the filing excerpts."
            )

        _prompt = build_prompt(query, structured_context, retrieved_context)
        _ = SYSTEM_PROMPT, _prompt
        return RagResponse(
            query_type=query_type,
            answer=answer,
            structured_context=structured_context,
            retrieved_context=retrieved_context,
        )


def main() -> None:
    engine = FinancialRAGEngine()
    print("Financial RAG shell")
    print("Type a question, or 'exit' to quit.\n")
    while True:
        query = input("You: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Chatbot: Goodbye.")
            break
        response = engine.generate_answer(query)
        print(f"Chatbot: {response.answer}")
        if response.structured_context:
            print("\nStructured context:\n" + response.structured_context)
        print("\nRetrieved context:\n" + response.retrieved_context)


if __name__ == "__main__":
    main()
