from pathlib import Path

import pandas as pd

from dashboard import streamlit_app
from dashboard.streamlit_app import (
    HISTORICAL_NARRATIVE_PATH,
    WATCHLIST_INDICATORS_PATH,
    choose_return_metric,
    filter_historical_data,
    find_processed_snapshots,
    load_csv_if_exists,
    load_historical_narrative_data,
    load_snapshot_data,
    load_watchlist_data,
    prepare_latest_watchlist_table,
    validate_historical_data,
    validate_watchlist_data,
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


def test_historical_csv_path_points_to_processed_historical_output() -> None:
    assert HISTORICAL_NARRATIVE_PATH.as_posix().endswith(
        "data/processed/historical/narrative_market_history_90d.csv"
    )


def test_watchlist_csv_path_points_to_processed_historical_output() -> None:
    assert WATCHLIST_INDICATORS_PATH.as_posix().endswith(
        "data/processed/historical/narrative_watchlist_indicators_90d.csv"
    )


def test_validate_historical_data_passes_with_required_columns() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-05-21"]),
            "primary_narrative": ["Layer 1"],
        }
    )

    assert validate_historical_data(df) == []


def test_validate_historical_data_fails_gracefully_when_required_columns_missing() -> None:
    df = pd.DataFrame({"date": pd.to_datetime(["2026-05-21"])})

    warnings = validate_historical_data(df)

    assert warnings
    assert "primary_narrative" in warnings[0]


def test_validate_historical_data_warns_when_file_is_missing() -> None:
    warnings = validate_historical_data(None)

    assert warnings
    assert "narrative_market_history_90d.csv" in warnings[0]


def test_choose_return_metric_prefers_7d_then_falls_back_to_30d() -> None:
    assert choose_return_metric(pd.DataFrame(columns=["avg_return_7d", "avg_return_30d"])) == "avg_return_7d"
    assert choose_return_metric(pd.DataFrame(columns=["avg_return_30d"])) == "avg_return_30d"
    assert choose_return_metric(pd.DataFrame(columns=["median_return_7d"])) is None


def test_filter_historical_data_applies_narrative_and_date_range() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-05-20", "2026-05-21", "2026-05-22"]),
            "primary_narrative": ["Layer 1", "DeFi", "Layer 1"],
            "avg_return_7d": [0.1, 0.2, 0.3],
        }
    )

    filtered = filter_historical_data(
        df,
        selected_narratives=["Layer 1"],
        date_range=(pd.Timestamp("2026-05-21").date(), pd.Timestamp("2026-05-22").date()),
    )

    assert filtered["primary_narrative"].tolist() == ["Layer 1"]
    assert filtered["date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-05-22"]


def test_load_historical_narrative_data_parses_date(tmp_path: Path) -> None:
    csv_path = tmp_path / "narrative_market_history_90d.csv"
    csv_path.write_text(
        "date,primary_narrative,avg_return_7d\n2026-05-22,Layer 1,0.1\n",
        encoding="utf-8",
    )

    df = load_historical_narrative_data(csv_path)

    assert df is not None
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_load_watchlist_data_returns_none_when_file_is_missing(tmp_path: Path) -> None:
    assert load_watchlist_data(tmp_path / "missing_watchlist.csv") is None


def test_load_watchlist_data_parses_date(tmp_path: Path) -> None:
    csv_path = tmp_path / "narrative_watchlist_indicators_90d.csv"
    csv_path.write_text(
        "date,primary_narrative,watchlist_score,watch_volume_accel,"
        "watch_breadth_expand,watch_quiet_rs,watch_momentum_pickup,watchlist_label\n"
        "2026-05-22,Layer 1,2,True,False,True,False,Monitor\n",
        encoding="utf-8",
    )

    df = load_watchlist_data(csv_path)

    assert df is not None
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_validate_watchlist_data_warns_when_file_is_missing() -> None:
    warnings = validate_watchlist_data(None)

    assert warnings
    assert "Narrative Watchlist data is not available yet" in warnings[0]
    assert "narrative_watchlist_indicators_90d.csv" in warnings[0]


def test_validate_watchlist_data_warns_when_required_columns_missing() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-05-21"]),
            "primary_narrative": ["Layer 1"],
            "watchlist_score": [1],
        }
    )

    warnings = validate_watchlist_data(df)

    assert warnings
    assert "watch_volume_accel" in warnings[0]
    assert "watchlist_label" in warnings[0]


def test_validate_watchlist_data_passes_with_required_columns() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-05-21"]),
            "primary_narrative": ["Layer 1"],
            "watchlist_score": [1],
            "watch_volume_accel": [False],
            "watch_breadth_expand": [False],
            "watch_quiet_rs": [True],
            "watch_momentum_pickup": [False],
            "watchlist_label": ["Low Research Interest"],
        }
    )

    assert validate_watchlist_data(df) == []


def test_prepare_latest_watchlist_table_sorts_and_formats_booleans() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2026-05-20", "2026-05-21", "2026-05-21"]
            ),
            "primary_narrative": ["AI", "AI", "DeFi"],
            "watchlist_score": [1, 2, 3],
            "watch_volume_accel": [False, True, False],
            "watch_breadth_expand": [False, False, True],
            "watch_quiet_rs": [True, True, True],
            "watch_momentum_pickup": [False, False, True],
            "watchlist_label": [
                "Low Research Interest",
                "Monitor",
                "Review Closely",
            ],
        }
    )

    table = prepare_latest_watchlist_table(df)

    assert table["Narrative"].tolist() == ["DeFi", "AI"]
    assert table["Watchlist Score"].tolist() == [3, 2]
    assert table["Vol Accel"].tolist() == ["No", "Yes"]
    assert table["Breadth Expand"].tolist() == ["Yes", "No"]
    assert table["Research Label"].tolist() == ["Review Closely", "Monitor"]
