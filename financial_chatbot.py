from pathlib import Path
import re

import pandas as pd


BASE_PATH = Path(__file__).resolve().parent
CSV_FILES = [
    BASE_PATH / "microsoft_10k_financials_2023_2025.csv",
    BASE_PATH / "tesla_10k_financials_2023_2025.csv",
    BASE_PATH / "apple_10k_financials_2023_2025.csv",
]

METRIC_COLUMNS = [
    "total_revenue_musd",
    "net_income_musd",
    "total_assets_musd",
    "total_liabilities_musd",
    "cash_flow_from_operating_activities_musd",
]


def load_financial_data() -> pd.DataFrame:
    frames = [pd.read_csv(file_path) for file_path in CSV_FILES]
    data = pd.concat(frames, ignore_index=True)
    data["period_end"] = pd.to_datetime(data["period_end"])
    data = data.sort_values(["company", "fiscal_year"]).reset_index(drop=True)
    return data


def format_musd(value: float) -> str:
    return f"{value:,.0f} million USD"


def latest_year_value(data: pd.DataFrame, company: str, column: str) -> float:
    company_data = data[data["company"] == company].sort_values("fiscal_year")
    return float(company_data.iloc[-1][column])


def yoy_change_pct(data: pd.DataFrame, company: str, column: str) -> float:
    company_data = data[data["company"] == company].sort_values("fiscal_year")
    previous_value = float(company_data.iloc[-2][column])
    latest_value = float(company_data.iloc[-1][column])
    return ((latest_value - previous_value) / previous_value) * 100


def latest_year_label(data: pd.DataFrame, company: str) -> int:
    company_data = data[data["company"] == company].sort_values("fiscal_year")
    return int(company_data.iloc[-1]["fiscal_year"])


def simple_chatbot(user_query: str) -> str:
    data = load_financial_data()
    query = re.sub(r"\s+", " ", user_query.strip().lower())

    if query in {"what is the total revenue?", "what is the total revenue", "total revenue"}:
        latest_year = latest_year_label(data, "Microsoft")
        microsoft_revenue = latest_year_value(data, "Microsoft", "total_revenue_musd")
        tesla_revenue = latest_year_value(data, "Tesla", "total_revenue_musd")
        apple_revenue = latest_year_value(data, "Apple", "total_revenue_musd")
        combined = microsoft_revenue + tesla_revenue + apple_revenue
        return (
            f"Latest-year total revenue for FY{latest_year} is Microsoft {format_musd(microsoft_revenue)}, "
            f"Tesla {format_musd(tesla_revenue)}, and Apple {format_musd(apple_revenue)}. "
            f"Combined total revenue is {format_musd(combined)}."
        )

    elif query in {
        "how has net income changed over the last year?",
        "how has net income changed over the last year",
        "net income change",
    }:
        microsoft_change = yoy_change_pct(data, "Microsoft", "net_income_musd")
        tesla_change = yoy_change_pct(data, "Tesla", "net_income_musd")
        apple_change = yoy_change_pct(data, "Apple", "net_income_musd")
        return (
            "From FY2024 to FY2025, net income changed by "
            f"Microsoft {microsoft_change:+.1f}%, Tesla {tesla_change:+.1f}%, and Apple {apple_change:+.1f}%."
        )

    elif query in {"what are the total assets?", "what are the total assets", "total assets"}:
        latest_year = latest_year_label(data, "Microsoft")
        microsoft_assets = latest_year_value(data, "Microsoft", "total_assets_musd")
        tesla_assets = latest_year_value(data, "Tesla", "total_assets_musd")
        apple_assets = latest_year_value(data, "Apple", "total_assets_musd")
        combined = microsoft_assets + tesla_assets + apple_assets
        return (
            f"Latest-year total assets for FY{latest_year} are Microsoft {format_musd(microsoft_assets)}, "
            f"Tesla {format_musd(tesla_assets)}, and Apple {format_musd(apple_assets)}. "
            f"Combined total assets are {format_musd(combined)}."
        )

    elif query in {"what are the total liabilities?", "what are the total liabilities", "total liabilities"}:
        latest_year = latest_year_label(data, "Microsoft")
        microsoft_liabilities = latest_year_value(data, "Microsoft", "total_liabilities_musd")
        tesla_liabilities = latest_year_value(data, "Tesla", "total_liabilities_musd")
        apple_liabilities = latest_year_value(data, "Apple", "total_liabilities_musd")
        combined = microsoft_liabilities + tesla_liabilities + apple_liabilities
        return (
            f"Latest-year total liabilities for FY{latest_year} are Microsoft {format_musd(microsoft_liabilities)}, "
            f"Tesla {format_musd(tesla_liabilities)}, and Apple {format_musd(apple_liabilities)}. "
            f"Combined total liabilities are {format_musd(combined)}."
        )

    elif query in {
        "what is the cash flow from operating activities?",
        "what is the cash flow from operating activities",
        "operating cash flow",
    }:
        latest_year = latest_year_label(data, "Microsoft")
        microsoft_cfo = latest_year_value(data, "Microsoft", "cash_flow_from_operating_activities_musd")
        tesla_cfo = latest_year_value(data, "Tesla", "cash_flow_from_operating_activities_musd")
        apple_cfo = latest_year_value(data, "Apple", "cash_flow_from_operating_activities_musd")
        combined = microsoft_cfo + tesla_cfo + apple_cfo
        return (
            f"Latest-year cash flow from operating activities for FY{latest_year} is Microsoft {format_musd(microsoft_cfo)}, "
            f"Tesla {format_musd(tesla_cfo)}, and Apple {format_musd(apple_cfo)}. "
            f"Combined operating cash flow is {format_musd(combined)}."
        )

    else:
        return (
            "Sorry, I can only answer the predefined financial queries about total revenue, "
            "net income change, total assets, total liabilities, and operating cash flow."
        )


def main() -> None:
    print("Financial Analysis Chatbot")
    print("Type one of the predefined questions below, or type 'exit' to quit.\n")
    print("Supported queries:")
    print("- What is the total revenue?")
    print("- How has net income changed over the last year?")
    print("- What are the total assets?")
    print("- What are the total liabilities?")
    print("- What is the cash flow from operating activities?\n")

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in {"exit", "quit"}:
            print("Chatbot: Goodbye.")
            break
        print(f"Chatbot: {simple_chatbot(user_query)}")


if __name__ == "__main__":
    main()
