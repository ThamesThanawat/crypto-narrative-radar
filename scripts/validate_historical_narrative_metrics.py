"""Validate processed historical narrative metrics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.config import PROCESSED_DATA_DIR
from crypto_narrative_radar.metrics.historical_narrative_metrics import (
    HISTORICAL_NARRATIVE_COLUMNS,
    HISTORICAL_NARRATIVE_FILENAME,
)


DEFAULT_HISTORY_PATH = (
    PROCESSED_DATA_DIR / "historical" / HISTORICAL_NARRATIVE_FILENAME
)
NUMERIC_COLUMNS = [
    column
    for column in HISTORICAL_NARRATIVE_COLUMNS
    if column not in {"date", "primary_narrative", "top_token_by_market_cap", "concentration_flag"}
]
VALID_CONCENTRATION_FLAGS = {"Low", "Medium", "High", "Unknown"}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate processed historical narrative metrics."
    )
    parser.add_argument("--path", type=Path, default=DEFAULT_HISTORY_PATH)
    return parser.parse_args()


def _is_numeric_or_nullable(series: pd.Series) -> bool:
    numeric = pd.to_numeric(series, errors="coerce")
    return bool(series.isna().equals(numeric.isna()))


def validate_historical_narrative_metrics(
    path: Path,
) -> tuple[list[str], list[str], pd.DataFrame]:
    """Validate a historical narrative metrics CSV."""
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"Historical narrative metrics file not found: {path}"], warnings, pd.DataFrame()

    df = pd.read_csv(path)
    if df.empty:
        errors.append("Historical narrative metrics are empty.")
        return errors, warnings, df

    missing_columns = [
        column for column in HISTORICAL_NARRATIVE_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        return errors, warnings, df

    if df.duplicated(subset=["date", "primary_narrative"]).any():
        errors.append("Duplicate rows found for date + primary_narrative.")

    parsed_dates = pd.to_datetime(df["date"], errors="coerce")
    if parsed_dates.isna().any():
        errors.append("date contains invalid values.")

    for column in NUMERIC_COLUMNS:
        if not _is_numeric_or_nullable(df[column]):
            errors.append(f"{column} must be numeric or nullable.")

    unexpected_flags = sorted(
        set(df["concentration_flag"].dropna()) - VALID_CONCENTRATION_FLAGS
    )
    if unexpected_flags:
        errors.append(
            "Unexpected concentration_flag values: " + ", ".join(unexpected_flags)
        )

    if df["primary_narrative"].isna().any():
        errors.append("primary_narrative contains null values.")
    if (pd.to_numeric(df["token_count"], errors="coerce") <= 0).any():
        errors.append("token_count must be positive.")

    expected_rows = df["date"].nunique() * df["primary_narrative"].nunique()
    if len(df) != expected_rows:
        warnings.append(
            "Not every narrative appears on every date. Review missing token history if unexpected."
        )
    for column in ["breadth_7d", "breadth_30d", "relative_strength_7d"]:
        if df[column].isna().any():
            warnings.append(
                f"{column} contains null values; early rows may have incomplete lag history."
            )

    return errors, warnings, df


def main() -> int:
    """Validate historical narrative metrics."""
    args = parse_args()
    errors, warnings, df = validate_historical_narrative_metrics(args.path)

    print("Historical narrative metrics validation summary")
    print(f"File: {args.path}")
    print(f"Rows: {len(df)}")
    if not df.empty and "date" in df:
        parsed_dates = pd.to_datetime(df["date"], errors="coerce").dropna()
        if not parsed_dates.empty:
            print(f"Date range: {parsed_dates.min().date()} to {parsed_dates.max().date()}")
    if not df.empty and "primary_narrative" in df:
        print(f"Narratives: {df['primary_narrative'].nunique()}")

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
