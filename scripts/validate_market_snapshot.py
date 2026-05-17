"""Validate a processed token market snapshot CSV."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.config import PROCESSED_DATA_DIR


REQUIRED_COLUMNS = [
    "coingecko_id",
    "symbol",
    "name",
    "current_price",
    "market_cap",
    "total_volume",
    "price_change_percentage_24h",
    "price_change_percentage_7d_in_currency",
    "price_change_percentage_30d_in_currency",
    "last_updated",
    "primary_narrative",
    "secondary_narratives",
    "include_in_score",
    "notes",
]
PRICE_COLUMNS = ["current_price", "market_cap", "total_volume"]


def find_latest_snapshot() -> Path:
    """Find the latest processed market snapshot by dated folder name."""
    snapshot_paths = sorted(
        PROCESSED_DATA_DIR.glob("*/token_market_snapshot_*.csv"),
        key=lambda path: path.parent.name,
    )
    if not snapshot_paths:
        raise FileNotFoundError("No processed market snapshot CSV found.")
    return snapshot_paths[-1]


def _is_blank(series: pd.Series) -> pd.Series:
    return series.isna() | (series.astype(str).str.strip() == "")


def validate_snapshot(path: Path) -> tuple[list[str], list[str], pd.DataFrame]:
    """Return validation errors, warnings, and loaded snapshot data."""
    snapshot = pd.read_csv(path)
    errors: list[str] = []
    warnings: list[str] = []

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in snapshot.columns
    ]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        return errors, warnings, snapshot

    if snapshot.empty:
        errors.append("Market snapshot is empty.")

    for column in ["coingecko_id", "primary_narrative"]:
        if _is_blank(snapshot[column]).any():
            errors.append(f"{column} contains empty values.")

    if snapshot["coingecko_id"].astype(str).str.lower().duplicated().any():
        errors.append("Duplicate coingecko_id values found.")

    for column in PRICE_COLUMNS:
        if snapshot[column].isna().any():
            warnings.append(f"{column} contains null values.")

    return errors, warnings, snapshot


def main() -> int:
    """Validate a provided snapshot path, or the latest processed snapshot."""
    snapshot_path = Path(sys.argv[1]) if len(sys.argv) > 1 else find_latest_snapshot()
    errors, warnings, snapshot = validate_snapshot(snapshot_path)

    print("Market snapshot validation summary")
    print(f"File: {snapshot_path}")
    print(f"Rows: {len(snapshot)}")
    print(f"Columns: {len(snapshot.columns)}")

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
    sys.exit(main())
