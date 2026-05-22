"""Calculate daily historical narrative-level market metrics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.metrics.historical_narrative_metrics import (
    HISTORICAL_NARRATIVE_FILENAME,
    HISTORICAL_TOKEN_FILENAME,
    build_historical_narrative_metrics,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate historical narrative metrics from token history."
    )
    parser.add_argument("--input-name", default=HISTORICAL_TOKEN_FILENAME)
    parser.add_argument("--output-name", default=HISTORICAL_NARRATIVE_FILENAME)
    return parser.parse_args()


def main() -> int:
    """Run historical narrative metric calculation."""
    args = parse_args()
    metrics_df, output_path = build_historical_narrative_metrics(
        input_name=args.input_name,
        output_name=args.output_name,
    )

    print("Historical narrative metrics calculation")
    print(f"Rows: {len(metrics_df)}")
    print(f"Dates: {metrics_df['date'].nunique()}")
    print(f"Narratives: {metrics_df['primary_narrative'].nunique()}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
