"""Validate narrative metrics and ranking CSVs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.config import PROCESSED_DATA_DIR
from crypto_narrative_radar.metrics.narrative_metrics import (
    NARRATIVE_METRICS_FILENAME,
    NARRATIVE_RANKING_FILENAME,
    find_latest_processed_date,
    get_snapshot_path,
)


BREADTH_COLUMNS = ["breadth_24h", "breadth_7d", "breadth_30d"]
SCORE_COLUMNS = [
    "price_momentum_score",
    "volume_confirmation_score",
    "breadth_score",
    "relative_strength_score",
    "narrative_momentum_score",
]
REQUIRED_RANKING_COLUMNS = ["rank", "primary_narrative", "scoring_note"]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Validate narrative metric outputs.")
    parser.add_argument(
        "--date",
        help="Processed snapshot date folder, for example 2026-05-17.",
    )
    return parser.parse_args()


def _has_infinite_values(df: pd.DataFrame) -> bool:
    numeric_df = df.select_dtypes(include="number")
    return bool(numeric_df.isin([float("inf"), float("-inf")]).any().any())


def _between_zero_and_one(series: pd.Series) -> bool:
    numeric = pd.to_numeric(series, errors="coerce")
    numeric = numeric.dropna()
    if numeric.empty:
        return True
    return bool(((numeric >= 0) & (numeric <= 1)).all())


def _between_zero_and_100(series: pd.Series) -> bool:
    numeric = pd.to_numeric(series, errors="coerce")
    numeric = numeric.dropna()
    if numeric.empty:
        return True
    return bool(((numeric >= 0) & (numeric <= 100)).all())


def validate_outputs(run_date: str) -> tuple[list[str], pd.DataFrame, pd.DataFrame]:
    """Validate narrative output files for a processed snapshot date."""
    errors: list[str] = []
    output_dir = PROCESSED_DATA_DIR / run_date
    snapshot_path = get_snapshot_path(run_date)
    metrics_path = output_dir / NARRATIVE_METRICS_FILENAME
    ranking_path = output_dir / NARRATIVE_RANKING_FILENAME

    if not metrics_path.exists():
        errors.append(f"Missing narrative metrics file: {metrics_path}")
        return errors, pd.DataFrame(), pd.DataFrame()
    if not ranking_path.exists():
        errors.append(f"Missing narrative ranking file: {ranking_path}")
        return errors, pd.DataFrame(), pd.DataFrame()
    if not snapshot_path.exists():
        errors.append(f"Missing token snapshot file: {snapshot_path}")
        return errors, pd.DataFrame(), pd.DataFrame()

    metrics = pd.read_csv(metrics_path)
    ranking = pd.read_csv(ranking_path)
    snapshot = pd.read_csv(snapshot_path)

    if metrics.empty:
        errors.append("narrative_metrics.csv is empty.")
    if ranking.empty:
        errors.append("narrative_ranking.csv is empty.")

    missing_ranking_columns = [
        column for column in REQUIRED_RANKING_COLUMNS if column not in ranking.columns
    ]
    if missing_ranking_columns:
        errors.append(
            "Ranking missing required columns: " + ", ".join(missing_ranking_columns)
        )

    unique_narratives = snapshot["primary_narrative"].nunique()
    if len(metrics) != unique_narratives:
        errors.append("Metrics row count does not match snapshot narrative count.")
    if len(ranking) != unique_narratives:
        errors.append("Ranking row count does not match snapshot narrative count.")

    for label, df in [("metrics", metrics), ("ranking", ranking)]:
        if "primary_narrative" in df and df["primary_narrative"].duplicated().any():
            errors.append(f"{label} has duplicate primary_narrative values.")
        if "token_count" in df and (df["token_count"] <= 0).any():
            errors.append(f"{label} has non-positive token_count values.")
        for column in ["total_market_cap", "total_volume"]:
            if column in df and (pd.to_numeric(df[column], errors="coerce") < 0).any():
                errors.append(f"{label} has negative {column} values.")
        for column in BREADTH_COLUMNS:
            if column in df and not _between_zero_and_one(df[column]):
                errors.append(f"{label} has {column} outside 0 to 1.")
        for column in SCORE_COLUMNS:
            if column in df and not _between_zero_and_100(df[column]):
                errors.append(f"{label} has {column} outside 0 to 100.")
        if _has_infinite_values(df):
            errors.append(f"{label} contains infinite values.")

    if "narrative_momentum_score" in ranking:
        scores = ranking["narrative_momentum_score"]
        if not scores.is_monotonic_decreasing:
            errors.append("Ranking is not sorted by narrative_momentum_score descending.")
    if "rank" in ranking:
        expected_rank = list(range(1, len(ranking) + 1))
        if ranking["rank"].tolist() != expected_rank:
            errors.append("Rank does not start at 1 and increase by 1.")
        if ranking["rank"].duplicated().any():
            errors.append("Rank values are not unique.")
    else:
        errors.append("Ranking is missing rank column.")

    return errors, metrics, ranking


def main() -> int:
    """Validate narrative metric outputs."""
    args = parse_args()
    run_date = args.date or find_latest_processed_date()
    errors, metrics, ranking = validate_outputs(run_date)

    print("Narrative metrics validation summary")
    print(f"Run date: {run_date}")
    print(f"Metrics rows: {len(metrics)}")
    print(f"Ranking rows: {len(ranking)}")

    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation errors: none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
