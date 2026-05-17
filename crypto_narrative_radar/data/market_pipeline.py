"""CoinGecko market data pipeline."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from crypto_narrative_radar.api.coingecko import fetch_markets
from crypto_narrative_radar.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from crypto_narrative_radar.data.loaders import load_taxonomy


MARKET_COLUMNS = [
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
]
TAXONOMY_COLUMNS = [
    "coingecko_id",
    "symbol",
    "name",
    "primary_narrative",
    "secondary_narratives",
    "include_in_score",
    "notes",
]
PROCESSED_COLUMNS = [
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
    "market_symbol",
    "market_name",
]


def get_taxonomy_ids(taxonomy_df: pd.DataFrame) -> list[str]:
    """Return clean CoinGecko IDs from the taxonomy."""
    if "coingecko_id" not in taxonomy_df.columns:
        raise ValueError("Taxonomy is missing required column: coingecko_id")

    coingecko_ids = taxonomy_df["coingecko_id"].dropna().astype(str).str.strip()
    coingecko_ids = coingecko_ids[coingecko_ids != ""].tolist()
    if not coingecko_ids:
        raise ValueError("Taxonomy does not contain any CoinGecko IDs.")

    return coingecko_ids


def save_raw_market_data(
    raw_data: list[dict],
    run_date: date,
    base_dir: Path = RAW_DATA_DIR,
) -> Path:
    """Save raw CoinGecko market data to a date-partitioned CSV."""
    output_dir = base_dir / "coingecko" / "markets" / run_date.isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"coingecko_markets_raw_{run_date.isoformat()}.csv"
    pd.DataFrame(raw_data).to_csv(output_path, index=False)
    return output_path


def normalize_market_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Normalize raw CoinGecko market data into stable token-level columns."""
    if raw_df.empty:
        raise ValueError("Raw market data is empty.")
    if "id" not in raw_df.columns:
        raise ValueError("Raw market data is missing required column: id")

    market_df = raw_df.rename(columns={"id": "coingecko_id"}).copy()
    for column in MARKET_COLUMNS:
        if column not in market_df.columns:
            market_df[column] = pd.NA

    return market_df[MARKET_COLUMNS]


def merge_with_taxonomy(
    market_df: pd.DataFrame,
    taxonomy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge normalized market data with taxonomy metadata."""
    missing_columns = [
        column for column in TAXONOMY_COLUMNS if column not in taxonomy_df.columns
    ]
    if missing_columns:
        raise ValueError(f"Taxonomy missing columns: {', '.join(missing_columns)}")

    market_for_merge = market_df.rename(
        columns={"symbol": "market_symbol", "name": "market_name"}
    )
    taxonomy_for_merge = taxonomy_df[TAXONOMY_COLUMNS].copy()

    merged = market_for_merge.merge(
        taxonomy_for_merge,
        on="coingecko_id",
        how="left",
        validate="one_to_one",
    )

    for column in PROCESSED_COLUMNS:
        if column not in merged.columns:
            merged[column] = pd.NA

    return merged[PROCESSED_COLUMNS]


def save_processed_market_snapshot(
    df: pd.DataFrame,
    run_date: date,
    base_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Save a processed token market snapshot to a date-partitioned CSV."""
    output_dir = base_dir / run_date.isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"token_market_snapshot_{run_date.isoformat()}.csv"
    df.to_csv(output_path, index=False)
    return output_path


def build_market_snapshot(run_date: date | None = None) -> pd.DataFrame:
    """Fetch, normalize, merge, and save the current token market snapshot."""
    snapshot_date = run_date or date.today()
    taxonomy_df = load_taxonomy()
    coingecko_ids = get_taxonomy_ids(taxonomy_df)
    raw_data = fetch_markets(coingecko_ids)
    save_raw_market_data(raw_data, snapshot_date)
    market_df = normalize_market_data(pd.DataFrame(raw_data))
    snapshot_df = merge_with_taxonomy(market_df, taxonomy_df)
    save_processed_market_snapshot(snapshot_df, snapshot_date)
    return snapshot_df
