from pathlib import Path

from dashboard import streamlit_app
from dashboard.streamlit_app import (
    find_processed_snapshots,
    load_csv_if_exists,
    load_snapshot_data,
)


def test_find_processed_snapshots_returns_date_folders_descending(tmp_path: Path) -> None:
    (tmp_path / "2026-05-18").mkdir()
    (tmp_path / "not-a-date").mkdir()
    (tmp_path / "2026-05-19").mkdir()

    assert find_processed_snapshots(tmp_path) == ["2026-05-19", "2026-05-18"]


def test_load_csv_if_exists_returns_none_for_missing_file(tmp_path: Path) -> None:
    assert load_csv_if_exists(tmp_path / "missing.csv") is None


def test_dashboard_file_exists() -> None:
    assert Path("dashboard/streamlit_app.py").exists()


def test_requirements_include_streamlit_and_plotly() -> None:
    requirements = Path("requirements.txt").read_text(encoding="utf-8").splitlines()

    assert "streamlit" in requirements
    assert "plotly" in requirements


def test_load_snapshot_data_allows_missing_optional_files(tmp_path: Path, monkeypatch) -> None:
    snapshot_dir = tmp_path / "2026-05-19"
    snapshot_dir.mkdir()
    (snapshot_dir / "narrative_ranking.csv").write_text(
        "primary_narrative,narrative_momentum_score\nLayer 1,80\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(streamlit_app, "PROCESSED_DATA_DIR", tmp_path)

    data = load_snapshot_data("2026-05-19")

    assert data["ranking"] is not None
    assert data["contributors"] is None
    assert data["concentration"] is None
