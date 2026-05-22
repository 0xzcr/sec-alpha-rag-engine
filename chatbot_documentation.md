# Financial Analysis Chatbot Documentation

## Overview

This project is a lightweight, rule-based chatbot built from the financial data collected in Task 1.  
It is intentionally simple and uses `if` / `elif` logic to respond to a small set of predefined financial questions.

## Data Used

The chatbot reads these CSV files:

- `microsoft_10k_financials_2023_2025.csv`
- `tesla_10k_financials_2023_2025.csv`
- `apple_10k_financials_2023_2025.csv`

Each file contains:

- Total Revenue
- Net Income
- Total Assets
- Total Liabilities
- Cash Flow from Operating Activities

## How It Works

1. The script loads and combines the three CSV files using `pandas`.
2. It sorts the data by company and fiscal year.
3. The chatbot normalizes the user query by trimming whitespace and converting text to lowercase.
4. It checks the query against a fixed list of supported questions using `if` / `elif` statements.
5. For each supported query, it returns a canned response computed from the dataset.

## Supported Queries

- `What is the total revenue?`
- `How has net income changed over the last year?`
- `What are the total assets?`
- `What are the total liabilities?`
- `What is the cash flow from operating activities?`

## Example Responses

- Latest-year revenue across all three companies.
- Year-over-year percentage change in net income from FY2024 to FY2025.
- Latest-year total assets, liabilities, and operating cash flow by company.

## Limitations

- The chatbot only responds to the predefined questions.
- It does not perform semantic search or retrieval over the filings.
- It is not a generative AI or RAG-based system.
- It assumes the CSV files remain in the same folder as the script.

## How to Run

```bash
python3 financial_chatbot.py
```

Type one of the supported queries, or type `exit` to quit.
