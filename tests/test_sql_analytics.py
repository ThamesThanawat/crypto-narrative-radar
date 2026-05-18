from pathlib import Path

import duckdb
import pytest

from scripts.run_sql_analytics import (
    SQL_DIR,
    SQL_OUTPUTS,
    find_latest_processed_date,
    validate_inputs,
)
from scripts.validate_sql_outputs import validate_sql_outputs


def test_duckdb_dependency_imports() -> None:
    assert duckdb.__version__


def test_latest_processed_date_detection(tmp_path: Path) -> None:
    (tmp_path / "2026-05-17").mkdir()
    (tmp_path / "not-a-date").mkdir()
    (tmp_path / "2026-05-18").mkdir()

    assert find_latest_processed_date(tmp_path) == "2026-05-18"


def test_validate_inputs_returns_expected_paths(tmp_path: Path) -> None:
    processed_dir = tmp_path / "2026-05-17"
    processed_dir.mkdir()
    expected_files = [
        "token_market_snapshot_2026-05-17.csv",
        "narrative_metrics.csv",
        "narrative_ranking.csv",
    ]
    for filename in expected_files:
        (processed_dir / filename).write_text("primary_narrative\nLayer 1\n")

    input_paths = validate_inputs(processed_dir, "2026-05-17")

    assert set(input_paths) == {
        "token_market_snapshot",
        "narrative_metrics",
        "narrative_ranking",
    }


def test_validate_inputs_detects_missing_files(tmp_path: Path) -> None:
    processed_dir = tmp_path / "2026-05-17"
    processed_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        validate_inputs(processed_dir, "2026-05-17")


def test_sql_files_exist() -> None:
    for sql_filename in SQL_OUTPUTS:
        assert (SQL_DIR / sql_filename).exists()


def test_validate_sql_outputs_detects_missing_files(tmp_path: Path, monkeypatch) -> None:
    processed_dir = tmp_path / "2026-05-17"
    processed_dir.mkdir()

    monkeypatch.setattr(
        "scripts.run_sql_analytics.PROCESSED_DATA_DIR",
        tmp_path,
    )
    monkeypatch.setattr(
        "scripts.validate_sql_outputs.find_latest_processed_date",
        lambda: "2026-05-17",
    )
    monkeypatch.setattr(
        "scripts.validate_sql_outputs.get_processed_dir",
        lambda date_str: processed_dir,
    )

    errors, row_counts = validate_sql_outputs("2026-05-17")

    assert errors
    assert row_counts == {}
