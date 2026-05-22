"""Backfill token-level historical market data from CoinGecko."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.api.coingecko import (
    COINGECKO_BASE_URL,
    COINGECKO_MARKET_CHART_ENDPOINT,
)
from crypto_narrative_radar.data.historical import (
    build_failure_row,
    historical_raw_output_dir,
    normalize_historical_market_data,
    save_failure_log,
    save_processed_historical_data,
    save_raw_market_chart,
)
from crypto_narrative_radar.data.loaders import load_taxonomy


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Backfill token-level historical CoinGecko market data."
    )
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--vs-currency", default="usd")
    parser.add_argument("--interval", default="daily")
    parser.add_argument("--sleep-seconds", type=float, default=8.0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--limit-tokens", type=int)
    parser.add_argument("--token-id")
    parser.add_argument("--output-name", default="token_market_history_90d.csv")
    return parser.parse_args()


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def _clean_taxonomy(taxonomy_df: pd.DataFrame) -> pd.DataFrame:
    if "coingecko_id" not in taxonomy_df.columns:
        raise ValueError("Taxonomy is missing required column: coingecko_id")
    taxonomy = taxonomy_df.copy()
    taxonomy["coingecko_id"] = taxonomy["coingecko_id"].astype(str).str.strip()
    taxonomy = taxonomy[taxonomy["coingecko_id"] != ""].copy()
    if taxonomy.empty:
        raise ValueError("Taxonomy does not contain any CoinGecko IDs.")
    return taxonomy


def build_token_request_list(
    taxonomy_df: pd.DataFrame,
    token_id: str | None = None,
    limit_tokens: int | None = None,
) -> pd.DataFrame:
    """Build the token list for the historical backfill run."""
    taxonomy = _clean_taxonomy(taxonomy_df)
    if token_id:
        taxonomy = taxonomy[taxonomy["coingecko_id"] == token_id].copy()
        if taxonomy.empty:
            raise ValueError(f"Token ID not found in taxonomy: {token_id}")
    if limit_tokens is not None:
        taxonomy = taxonomy.head(limit_tokens).copy()
    return taxonomy.reset_index(drop=True)


def _request_market_chart_once(
    coingecko_id: str,
    vs_currency: str,
    days: int,
    interval: str,
    timeout: int = 30,
) -> requests.Response:
    endpoint = COINGECKO_MARKET_CHART_ENDPOINT.format(id=coingecko_id)
    url = f"{COINGECKO_BASE_URL}{endpoint}"
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": interval,
    }
    headers = {"User-Agent": "crypto-narrative-radar/0.1"}
    return requests.get(url, params=params, headers=headers, timeout=timeout)


def fetch_market_chart_with_retries(
    coingecko_id: str,
    vs_currency: str,
    days: int,
    interval: str,
    max_retries: int,
    sleep_seconds: float,
) -> tuple[dict[str, Any] | None, dict[str, object] | None]:
    """Fetch one market chart response, returning data or failure details."""
    last_failure: dict[str, object] | None = None

    for attempt in range(1, max_retries + 1):
        try:
            response = _request_market_chart_once(
                coingecko_id=coingecko_id,
                vs_currency=vs_currency,
                days=days,
                interval=interval,
            )
        except requests.Timeout as error:
            last_failure = {
                "error_type": "timeout",
                "status_code": None,
                "message": str(error),
                "attempt_count": attempt,
            }
        except requests.RequestException as error:
            last_failure = {
                "error_type": "network_error",
                "status_code": None,
                "message": str(error),
                "attempt_count": attempt,
            }
        else:
            status_code = response.status_code
            if status_code == 429 or 500 <= status_code < 600:
                last_failure = {
                    "error_type": "http_retryable",
                    "status_code": status_code,
                    "message": response.text[:300],
                    "attempt_count": attempt,
                }
            elif status_code >= 400:
                return None, {
                    "error_type": "http_error",
                    "status_code": status_code,
                    "message": response.text[:300],
                    "attempt_count": attempt,
                }
            else:
                try:
                    data = response.json()
                except ValueError as error:
                    last_failure = {
                        "error_type": "malformed_json",
                        "status_code": status_code,
                        "message": str(error),
                        "attempt_count": attempt,
                    }
                else:
                    if not isinstance(data, dict) or not data:
                        last_failure = {
                            "error_type": "empty_response",
                            "status_code": status_code,
                            "message": "CoinGecko returned an empty or invalid response.",
                            "attempt_count": attempt,
                        }
                    elif not any(data.get(key) for key in ["prices", "market_caps", "total_volumes"]):
                        last_failure = {
                            "error_type": "empty_response",
                            "status_code": status_code,
                            "message": "CoinGecko response contained no market chart arrays.",
                            "attempt_count": attempt,
                        }
                    else:
                        return data, None

        if attempt < max_retries:
            time.sleep(sleep_seconds * attempt)

    return None, last_failure


def main() -> int:
    """Run the historical CoinGecko token backfill."""
    args = parse_args()
    run_date = date.today()
    backfilled_at_utc = utc_now_iso()
    taxonomy_df = load_taxonomy()
    token_df = build_token_request_list(
        taxonomy_df,
        token_id=args.token_id,
        limit_tokens=args.limit_tokens,
    )

    responses: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, object]] = []

    for index, token in token_df.iterrows():
        coingecko_id = str(token["coingecko_id"])
        data, failure = fetch_market_chart_with_retries(
            coingecko_id=coingecko_id,
            vs_currency=args.vs_currency,
            days=args.days,
            interval=args.interval,
            max_retries=args.max_retries,
            sleep_seconds=args.sleep_seconds,
        )

        if data is not None:
            responses[coingecko_id] = data
            save_raw_market_chart(
                coingecko_id=coingecko_id,
                response=data,
                run_date=run_date,
                backfill_days=args.days,
                vs_currency=args.vs_currency,
                interval=args.interval,
                fetched_at_utc=utc_now_iso(),
            )
        else:
            failure = failure or {
                "error_type": "unknown_error",
                "status_code": None,
                "message": "Unknown CoinGecko request failure.",
                "attempt_count": args.max_retries,
            }
            failures.append(
                build_failure_row(
                    token=token,
                    error_type=str(failure["error_type"]),
                    status_code=failure.get("status_code"),
                    message=str(failure["message"]),
                    attempted_at_utc=utc_now_iso(),
                    attempt_count=int(failure["attempt_count"]),
                )
            )

        if index < len(token_df) - 1:
            time.sleep(args.sleep_seconds)

    processed_df = normalize_historical_market_data(
        responses=responses,
        taxonomy_df=token_df,
        backfill_days=args.days,
        interval=args.interval,
        backfilled_at_utc=backfilled_at_utc,
    )
    processed_path = save_processed_historical_data(
        processed_df,
        output_name=args.output_name,
    )
    failure_log_path = save_failure_log(failures, run_date=run_date)
    raw_output_dir = historical_raw_output_dir(run_date)

    print("CoinGecko historical token backfill")
    print(f"Requested token count: {len(token_df)}")
    print(f"Successful token count: {len(responses)}")
    print(f"Failed token count: {len(failures)}")
    print(f"Raw output folder: {raw_output_dir}")
    print(f"Processed output: {processed_path}")
    print(f"Failure log: {failure_log_path}")

    return 0 if responses else 1


if __name__ == "__main__":
    raise SystemExit(main())
