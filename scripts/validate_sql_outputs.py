"""Validate DuckDB SQL analytics output CSVs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_sql_analytics import (
    SQL_OUTPUTS,
    find_latest_processed_date,
    get_processed_dir,
)


EXPECTED_COLUMNS = {
    "sql_narrative_summary.csv": {"primary_narrative", "rank"},
    "sql_top_token_contributors.csv": {"primary_narrative", "symbol"},
    "sql_concentration_review.csv": {
        "primary_narrative",
        "concentration_comment",
    },
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Validate SQL analytics outputs.")
    parser.add_argument("--date", help="Processed folder date, for example 2026-05-17.")
    return parser.parse_args()


def validate_sql_outputs(date_str: str | None = None) -> tuple[list[str], dict[str, int]]:
    """Validate SQL output files and return errors plus row counts."""
    selected_date = date_str or find_latest_processed_date()
    processed_dir = get_processed_dir(selected_date)
    errors: list[str] = []
    row_counts: dict[str, int] = {}

    for output_filename in SQL_OUTPUTS.values():
        output_path = processed_dir / output_filename
        if not output_path.exists():
            errors.append(f"Missing SQL output file: {output_path}")
            continue

        df = pd.read_csv(output_path)
        row_counts[output_filename] = len(df)
        if df.empty:
            errors.append(f"{output_filename} is empty.")

        missing_columns = EXPECTED_COLUMNS[output_filename] - set(df.columns)
        if missing_columns:
            errors.append(
                f"{output_filename} missing column(s): "
                + ", ".join(sorted(missing_columns))
            )

        if (
            output_filename == "sql_narrative_summary.csv"
            and "primary_narrative" in df
            and df["primary_narrative"].duplicated().any()
        ):
            errors.append("sql_narrative_summary.csv has duplicate narratives.")

        if (
            output_filename == "sql_concentration_review.csv"
            and "primary_narrative" in df
            and df["primary_narrative"].duplicated().any()
        ):
            errors.append("sql_concentration_review.csv has duplicate narratives.")

    return errors, row_counts


def main() -> int:
    """Validate SQL output files for a processed date."""
    args = parse_args()
    selected_date = args.date or find_latest_processed_date()
    errors, row_counts = validate_sql_outputs(selected_date)

    print("SQL output validation summary")
    print(f"Run date: {selected_date}")
    for filename, row_count in row_counts.items():
        print(f"{filename}: {row_count} rows")

    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation errors: none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
