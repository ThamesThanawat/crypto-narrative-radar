"""Fetch CoinGecko market data and build a token market snapshot."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.api.coingecko import fetch_markets
from crypto_narrative_radar.data.loaders import load_taxonomy
from crypto_narrative_radar.data.market_pipeline import (
    get_taxonomy_ids,
    merge_with_taxonomy,
    normalize_market_data,
    save_processed_market_snapshot,
    save_raw_market_data,
)


def main() -> int:
    """Run the CoinGecko market pipeline for today's date."""
    run_date = date.today()
    taxonomy_df = load_taxonomy()
    requested_ids = get_taxonomy_ids(taxonomy_df)

    raw_data = fetch_markets(requested_ids)
    raw_path = save_raw_market_data(raw_data, run_date)

    market_df = normalize_market_data(pd.DataFrame(raw_data))
    snapshot_df = merge_with_taxonomy(market_df, taxonomy_df)
    processed_path = save_processed_market_snapshot(snapshot_df, run_date)

    returned_ids = set(market_df["coingecko_id"].dropna().astype(str))
    missing_ids = sorted(set(requested_ids) - returned_ids)

    print("CoinGecko market data pipeline")
    print(f"Run date: {run_date.isoformat()}")
    print(f"Requested taxonomy IDs: {len(requested_ids)}")
    print(f"Raw rows returned: {len(raw_data)}")
    print(f"Processed rows saved: {len(snapshot_df)}")
    print(f"Raw output: {raw_path}")
    print(f"Processed output: {processed_path}")

    if missing_ids:
        print("Missing taxonomy IDs from CoinGecko response:")
        for coingecko_id in missing_ids:
            print(f"- {coingecko_id}")
    else:
        print("Missing taxonomy IDs from CoinGecko response: none")

    return 0


if __name__ == "__main__":
    sys.exit(main())
