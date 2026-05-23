from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


COMPANY_ALIASES = {
    "Apple": ["apple", "aapl", "apple inc"],
    "Microsoft": ["microsoft", "msft", "microsoft corp", "microsoft corporation"],
    "Tesla": ["tesla", "tsla", "tesla inc", "tesla motors"],
}

METRIC_ALIASES = {
    "cash_flow_from_operating_activities_musd": [
        "cash flow from operating activities",
        "operating cash flow",
        "cash from operations",
        "cash generated from operations",
        "operating activities",
    ],
    "net_income_musd": [
        "net income",
        "earnings",
        "net earnings",
        "profit",
        "bottom line",
    ],
    "total_revenue_musd": [
        "revenue",
        "sales",
        "net sales",
        "turnover",
        "top line",
    ],
    "total_assets_musd": [
        "assets",
        "total assets",
        "asset base",
    ],
    "total_liabilities_musd": [
        "liabilities",
        "total liabilities",
        "debt and liabilities",
    ],
}

SNAPSHOT_KEYWORDS = [
    "financials",
    "finances",
    "financial performance",
    "financial position",
    "overview",
    "summary",
]

NARRATIVE_KEYWORDS = [
    "why",
    "how",
    "explain",
    "summarize",
    "summary",
    "risks",
    "risk",
    "outlook",
    "strategy",
    "management",
    "discussion",
    "business",
    "segment",
    "competition",
]

YEAR_PATTERN = re.compile(r"\b(20(?:23|24|25))\b")


@dataclass
class QueryPlan:
    query: str
    companies: list[str]
    years: list[int]
    metric: str | None
    mode: Literal["numeric", "narrative", "mixed"]
    retrieval_query: str
    snapshot_requested: bool
    assumption_note: str | None


def _match_alias(query: str, aliases: list[str]) -> bool:
    return any(alias in query for alias in aliases)


def detect_companies(query: str) -> list[str]:
    lowered = query.lower()
    return [company for company, aliases in COMPANY_ALIASES.items() if _match_alias(lowered, aliases)]


def detect_years(query: str) -> list[int]:
    return sorted({int(match.group(1)) for match in YEAR_PATTERN.finditer(query)})


def detect_metric(query: str) -> str | None:
    lowered = query.lower()
    for metric, aliases in METRIC_ALIASES.items():
        if _match_alias(lowered, aliases):
            return metric
    return None


def detect_snapshot_request(query: str) -> bool:
    lowered = query.lower()
    return any(keyword in lowered for keyword in SNAPSHOT_KEYWORDS)


def detect_narrative_request(query: str) -> bool:
    lowered = query.lower()
    return any(keyword in lowered for keyword in NARRATIVE_KEYWORDS)


def build_retrieval_query(
    query: str,
    companies: list[str],
    years: list[int],
    metric: str | None,
    snapshot_requested: bool,
) -> str:
    augmented_parts = [query]
    augmented_parts.extend(companies)
    augmented_parts.extend(str(year) for year in years)

    if metric:
        augmented_parts.append(metric.replace("_musd", "").replace("_", " "))
    elif snapshot_requested:
        augmented_parts.extend(
            [
                "revenue",
                "net income",
                "assets",
                "liabilities",
                "cash flow from operating activities",
            ]
        )

    augmented_parts.append("10-K")
    return " ".join(part for part in augmented_parts if part).strip()


def plan_query(query: str) -> QueryPlan:
    companies = detect_companies(query)
    years = detect_years(query)
    metric = detect_metric(query)
    snapshot_requested = detect_snapshot_request(query)
    narrative_request = detect_narrative_request(query)

    if metric or snapshot_requested:
        mode: Literal["numeric", "narrative", "mixed"] = "numeric"
    elif narrative_request:
        mode = "narrative"
    else:
        mode = "mixed"

    if snapshot_requested and not metric:
        assumption_note = "Interpreted 'financials' as a headline financial snapshot."
    elif metric == "net_income_musd" and "earnings" in query.lower():
        assumption_note = "Interpreted 'earnings' as net income."
    else:
        assumption_note = None

    retrieval_query = build_retrieval_query(query, companies, years, metric, snapshot_requested)

    return QueryPlan(
        query=query,
        companies=companies,
        years=years,
        metric=metric,
        mode=mode,
        retrieval_query=retrieval_query,
        snapshot_requested=snapshot_requested,
        assumption_note=assumption_note,
    )
