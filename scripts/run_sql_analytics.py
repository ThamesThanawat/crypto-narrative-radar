"""Run DuckDB SQL analytics over processed Crypto Narrative Radar CSVs."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.config import PROCESSED_DATA_DIR, PROJECT_ROOT


SQL_DIR = PROJECT_ROOT / "sql"
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SQL_OUTPUTS = {
    "01_narrative_summary.sql": "sql_narrative_summary.csv",
    "02_top_token_contributors.sql": "sql_top_token_contributors.csv",
    "03_concentration_review.sql": "sql_concentration_review.csv",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run DuckDB SQL analytics over processed CSV outputs."
    )
    parser.add_argument("--date", help="Processed folder date, for example 2026-05-17.")
    return parser.parse_args()


def find_latest_processed_date(base_dir: Path = PROCESSED_DATA_DIR) -> str:
    """Find the latest date-like processed folder."""
    date_dirs = [
        path.name
        for path in base_dir.iterdir()
        if path.is_dir() and DATE_PATTERN.match(path.name)
    ]
    if not date_dirs:
        raise FileNotFoundError(f"No date-like processed folders found in {base_dir}")
    return sorted(date_dirs)[-1]


def get_processed_dir(date_str: str | None = None) -> Path:
    """Return the processed folder for a date, or the latest processed date."""
    selected_date = date_str or find_latest_processed_date()
    return PROCESSED_DATA_DIR / selected_date


def validate_inputs(processed_dir: Path, date_str: str) -> dict[str, Path]:
    """Validate required processed CSV inputs and return their paths."""
    input_paths = {
        "token_market_snapshot": processed_dir
        / f"token_market_snapshot_{date_str}.csv",
        "narrative_metrics": processed_dir / "narrative_metrics.csv",
        "narrative_ranking": processed_dir / "narrative_ranking.csv",
    }
    missing_paths = [path for path in input_paths.values() if not path.exists()]
    if missing_paths:
        missing_text = "\n".join(f"- {path}" for path in missing_paths)
        raise FileNotFoundError(f"Missing required SQL input file(s):\n{missing_text}")
    return input_paths


def duckdb_path_literal(path: Path) -> str:
    """Return a DuckDB-safe quoted path literal."""
    normalized_path = path.resolve().as_posix().replace("'", "''")
    return f"'{normalized_path}'"


def register_csv_views(
    connection: duckdb.DuckDBPyConnection,
    input_paths: dict[str, Path],
) -> None:
    """Register processed CSV files as DuckDB views."""
    for view_name, csv_path in input_paths.items():
        connection.execute(
            f"""
            CREATE OR REPLACE VIEW {view_name} AS
            SELECT * FROM read_csv_auto({duckdb_path_literal(csv_path)}, header = true)
            """
        )


def run_sql_file(connection: duckdb.DuckDBPyConnection, sql_path: Path) -> object:
    """Execute a SQL file and return a DuckDB result relation."""
    sql_text = sql_path.read_text(encoding="utf-8")
    return connection.sql(sql_text)


def run_sql_analytics(date_str: str | None = None) -> dict[str, tuple[Path, int]]:
    """Run all SQL analytics files and export CSV outputs."""
    processed_dir = get_processed_dir(date_str)
    selected_date = processed_dir.name
    input_paths = validate_inputs(processed_dir, selected_date)
    results: dict[str, tuple[Path, int]] = {}

    with duckdb.connect(database=":memory:") as connection:
        register_csv_views(connection, input_paths)
        for sql_filename, output_filename in SQL_OUTPUTS.items():
            sql_path = SQL_DIR / sql_filename
            if not sql_path.exists():
                raise FileNotFoundError(f"Missing SQL file: {sql_path}")
            result_df = run_sql_file(connection, sql_path).df()
            output_path = processed_dir / output_filename
            result_df.to_csv(output_path, index=False)
            results[output_filename] = (output_path, len(result_df))

    return results


def main() -> int:
    """Run DuckDB SQL analytics and print output paths."""
    args = parse_args()
    try:
        results = run_sql_analytics(args.date)
    except (FileNotFoundError, duckdb.Error) as error:
        print(f"SQL analytics failed: {error}")
        return 1

    print("DuckDB SQL analytics")
    for output_name, (output_path, row_count) in results.items():
        print(f"{output_name}: {row_count} rows -> {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
