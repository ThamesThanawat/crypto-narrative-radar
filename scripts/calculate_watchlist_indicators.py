"""Generate narrative watchlist indicators from historical narrative metrics."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.config import PROCESSED_DATA_DIR
from crypto_narrative_radar.metrics.historical_narrative_metrics import (
    HISTORICAL_NARRATIVE_FILENAME,
)
from crypto_narrative_radar.metrics.watchlist_indicators import (
    WATCHLIST_OUTPUT_FILENAME,
    calculate_watchlist_indicators,
)


INPUT_PATH = PROCESSED_DATA_DIR / "historical" / HISTORICAL_NARRATIVE_FILENAME
OUTPUT_PATH = PROCESSED_DATA_DIR / "historical" / WATCHLIST_OUTPUT_FILENAME


def main() -> int:
    """Create narrative watchlist indicators and print a short summary."""
    if not INPUT_PATH.exists():
        print(f"Watchlist input file not found: {INPUT_PATH}")
        return 1

    try:
        history_df = pd.read_csv(INPUT_PATH)
        watchlist_df = calculate_watchlist_indicators(history_df)
    except ValueError as error:
        print(f"Watchlist indicator calculation failed: {error}")
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    watchlist_df.to_csv(OUTPUT_PATH, index=False)

    print("Narrative watchlist indicators")
    print(f"Rows: {len(watchlist_df)}")
    if not watchlist_df.empty:
        print(f"Date range: {watchlist_df['date'].min()} to {watchlist_df['date'].max()}")
        print(f"Narratives: {watchlist_df['primary_narrative'].nunique()}")
        print("Watchlist score distribution:")
        score_counts = watchlist_df["watchlist_score"].value_counts().sort_index()
        for score, count in score_counts.items():
            print(f"- {score}: {count}")
    else:
        print("Date range: n/a")
        print("Narratives: 0")
        print("Watchlist score distribution: none")
    print(f"Output: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
