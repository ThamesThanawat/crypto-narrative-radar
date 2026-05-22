"""Validate processed historical token market data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.api.coingecko import COINGECKO_MARKET_CHART_ENDPOINT
from crypto_narrative_radar.config import PROCESSED_DATA_DIR
from crypto_narrative_radar.data.historical import (
    HISTORICAL_OUTPUT_COLUMNS,
    VALID_QUALITY_FLAGS,
)


DEFAULT_HISTORY_PATH = (
    PROCESSED_DATA_DIR / "historical" / "token_market_history_90d.csv"
)
NUMERIC_COLUMNS = [
    "timestamp_ms",
    "price_usd",
    "market_cap_usd",
    "total_volume_usd",
    "volume_to_market_cap",
    "return_1d",
    "return_7d",
    "return_30d",
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate processed historical token market data."
    )
    parser.add_argument("--path", type=Path, default=DEFAULT_HISTORY_PATH)
    parser.add_argument("--days", type=int, default=90)
    return parser.parse_args()


def _is_numeric_or_nullable(series: pd.Series) -> bool:
    numeric = pd.to_numeric(series, errors="coerce")
    return bool(series.isna().equals(numeric.isna()))


def validate_historical_market_data(
    path: Path,
    expected_days: int = 90,
) -> tuple[list[str], list[str], pd.DataFrame]:
    """Validate a historical token market data CSV."""
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"Historical market data file not found: {path}"], warnings, pd.DataFrame()

    df = pd.read_csv(path)
    if df.empty:
        errors.append("Historical market data is empty.")
        return errors, warnings, df

    missing_columns = [
        column for column in HISTORICAL_OUTPUT_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        return errors, warnings, df

    if df.duplicated(subset=["coingecko_id", "date"]).any():
        errors.append("Duplicate rows found for coingecko_id + date.")

    parsed_dates = pd.to_datetime(df["date"], errors="coerce")
    if parsed_dates.isna().any():
        errors.append("date contains invalid values.")

    for column in NUMERIC_COLUMNS:
        if not _is_numeric_or_nullable(df[column]):
            errors.append(f"{column} must be numeric or nullable.")

    if not (df["source"] == "CoinGecko").all():
        errors.append("source must equal CoinGecko.")
    if not (df["endpoint"] == COINGECKO_MARKET_CHART_ENDPOINT).all():
        errors.append(f"endpoint must equal {COINGECKO_MARKET_CHART_ENDPOINT}.")
    if not (pd.to_numeric(df["backfill_days"], errors="coerce") == expected_days).all():
        errors.append(f"backfill_days must equal {expected_days}.")
    if not (df["interval"] == "daily").all():
        errors.append("interval must equal daily.")

    if df["data_quality_flag"].isna().any():
        errors.append("data_quality_flag contains null values.")
    unexpected_flags = sorted(set(df["data_quality_flag"].dropna()) - VALID_QUALITY_FLAGS)
    if unexpected_flags:
        errors.append("Unexpected data_quality_flag values: " + ", ".join(unexpected_flags))

    token_count = df["coingecko_id"].nunique()
    if token_count < 80:
        warnings.append(
            "Fewer than 80 tokens are present. Check the latest backfill_failures.csv "
            "if this was a full taxonomy run."
        )
    for column in ["return_7d", "return_30d"]:
        if df[column].isna().any():
            warnings.append(
                f"{column} contains null values; early rows may have incomplete lag history."
            )
    for column in ["market_cap_usd", "total_volume_usd"]:
        if df[column].isna().any():
            warnings.append(f"{column} contains null values.")

    return errors, warnings, df


def main() -> int:
    """Validate historical token market data."""
    args = parse_args()
    errors, warnings, df = validate_historical_market_data(args.path, args.days)

    print("Historical market data validation summary")
    print(f"File: {args.path}")
    print(f"Rows: {len(df)}")
    if not df.empty and "coingecko_id" in df:
        print(f"Token count: {df['coingecko_id'].nunique()}")
    if not df.empty and "date" in df:
        parsed_dates = pd.to_datetime(df["date"], errors="coerce").dropna()
        if not parsed_dates.empty:
            print(f"Date range: {parsed_dates.min().date()} to {parsed_dates.max().date()}")
    if not df.empty and "data_quality_flag" in df:
        print("Data quality flags:")
        for flag, count in df["data_quality_flag"].value_counts(dropna=False).items():
            print(f"- {flag}: {count}")

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("Warnings: none")

    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation errors: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
