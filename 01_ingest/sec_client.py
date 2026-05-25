import os
import time
from dataclasses import dataclass
from typing import Any

import requests

TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}


@dataclass
class SECClientConfig:
    user_agent: str
    timeout_seconds: int = 30
    max_retries: int = 4
    backoff_seconds: float = 1.5
    min_request_gap_seconds: float = 0.25


class SECClient:
    def __init__(self, config: SECClientConfig | None = None) -> None:
        user_agent = os.getenv(
            "SEC_USER_AGENT", "SecAlphaRagEngine contact@example.com"
        )
        self.config = config or SECClientConfig(user_agent=user_agent)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.config.user_agent,
                "Accept-Encoding": "gzip, deflate",
            }
        )
        self._last_request_ts = 0.0

    def _throttle(self) -> None:
        elapsed = time.time() - self._last_request_ts
        if elapsed < self.config.min_request_gap_seconds:
            time.sleep(self.config.min_request_gap_seconds - elapsed)
        self._last_request_ts = time.time()

    def _request(self, method: str, url: str, *, expected_json: bool = False) -> Any:
        last_error: Exception | None = None

        for attempt in range(1, self.config.max_retries + 1):
            self._throttle()
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=self.config.timeout_seconds,
                )
                if response.status_code in TRANSIENT_STATUS_CODES:
                    raise requests.HTTPError(
                        f"Transient SEC status {response.status_code} for {url}",
                        response=response,
                    )
                response.raise_for_status()
                return response.json() if expected_json else response.text
            except Exception as error:  # noqa: BLE001
                last_error = error
                status_code = getattr(
                    getattr(error, "response", None), "status_code", None
                )
                if (
                    status_code is not None
                    and status_code not in TRANSIENT_STATUS_CODES
                ):
                    raise
                if attempt < self.config.max_retries:
                    time.sleep(self.config.backoff_seconds * attempt)

        if last_error is not None:
            raise last_error
        raise RuntimeError(f"Unable to fetch {url}")

    def get_json(self, url: str) -> dict[str, Any]:
        result = self._request("GET", url, expected_json=True)
        assert isinstance(result, dict)
        return result

    def get_text(self, url: str) -> str:
        result = self._request("GET", url, expected_json=False)
        assert isinstance(result, str)
        return result

    def company_submissions(self, cik: str) -> dict[str, Any]:
        normalized_cik = cik.zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{normalized_cik}.json"
        return self.get_json(url)

    def company_facts(self, cik: str) -> dict[str, Any]:
        normalized_cik = cik.zfill(10)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{normalized_cik}.json"
        return self.get_json(url)

    @staticmethod
    def build_archive_url(
        cik: str, accession_number: str, primary_document: str
    ) -> str:
        accession_no_dashes = accession_number.replace("-", "")
        normalized_cik = cik.zfill(10).lstrip("0")
        return (
            f"https://www.sec.gov/Archives/edgar/data/{normalized_cik}/"
            f"{accession_no_dashes}/{primary_document}"
        )
