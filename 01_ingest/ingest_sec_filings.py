from __future__ import annotations

import csv
import json
from pathlib import Path

from config import COMPANIES, END_YEAR, MANIFEST_PATH, RAW_DATA_DIR, START_YEAR
from sec_client import SECClient


def ensure_output_dirs() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def select_10k_filings(submissions: dict, start_year: int, end_year: int) -> list[dict]:
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accession_numbers = recent.get("accessionNumber", [])
    filing_dates = recent.get("filingDate", [])
    primary_documents = recent.get("primaryDocument", [])
    primary_descriptions = recent.get("primaryDocDescription", [])

    filings: list[dict] = []
    for idx, form in enumerate(forms):
        if form != "10-K":
            continue

        filing_year = int(filing_dates[idx][:4])
        if filing_year < start_year or filing_year > end_year:
            continue

        filings.append(
            {
                "filing_year": filing_year,
                "accession_number": accession_numbers[idx],
                "filing_date": filing_dates[idx],
                "primary_document": primary_documents[idx],
                "primary_doc_description": primary_descriptions[idx]
                if idx < len(primary_descriptions)
                else "",
            }
        )

    return filings


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def ingest_company(
    client: SECClient, company: dict, start_year: int, end_year: int
) -> list[dict]:
    company_dir = RAW_DATA_DIR / company["ticker"].lower()
    company_dir.mkdir(parents=True, exist_ok=True)

    submissions = client.company_submissions(company["cik"])
    save_json(company_dir / "submissions.json", submissions)

    filings = select_10k_filings(submissions, start_year, end_year)
    manifest_rows: list[dict] = []

    for filing in filings:
        filing_dir = company_dir / str(filing["filing_year"])
        filing_dir.mkdir(parents=True, exist_ok=True)

        archive_url = client.build_archive_url(
            company["cik"],
            filing["accession_number"],
            filing["primary_document"],
        )
        filing_text = client.get_text(archive_url)

        filing_text_path = filing_dir / filing["primary_document"]
        filing_text_path.write_text(filing_text, encoding="utf-8")

        metadata = {
            "company": company["name"],
            "ticker": company["ticker"],
            "cik": company["cik"],
            **filing,
            "archive_url": archive_url,
            "local_path": str(filing_text_path),
        }
        save_json(filing_dir / "metadata.json", metadata)
        manifest_rows.append(metadata)

    return manifest_rows


def write_manifest(rows: list[dict]) -> None:
    fieldnames = [
        "company",
        "ticker",
        "cik",
        "filing_year",
        "filing_date",
        "accession_number",
        "primary_document",
        "primary_doc_description",
        "archive_url",
        "local_path",
    ]
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ensure_output_dirs()
    client = SECClient()

    all_rows: list[dict] = []
    for company in COMPANIES:
        all_rows.extend(ingest_company(client, company, START_YEAR, END_YEAR))

    write_manifest(all_rows)
    print(f"Ingest complete. Manifest saved to {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
