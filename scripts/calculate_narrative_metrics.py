"""Calculate narrative-level metrics and research rankings."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.metrics.narrative_metrics import (
    build_narrative_outputs,
    find_latest_processed_date,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate narrative metrics from a processed token snapshot."
    )
    parser.add_argument(
        "--date",
        help="Processed snapshot date folder, for example 2026-05-17.",
    )
    return parser.parse_args()


def main() -> int:
    """Run narrative metric calculation."""
    args = parse_args()
    run_date = args.date or find_latest_processed_date()
    metrics_df, ranking_df, metrics_path, ranking_path = build_narrative_outputs(
        run_date
    )

    print("Narrative metrics calculation")
    print(f"Run date: {run_date}")
    print(f"Narratives calculated: {len(metrics_df)}")
    print(f"Ranking rows: {len(ranking_df)}")
    print(f"Metrics output: {metrics_path}")
    print(f"Ranking output: {ranking_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
