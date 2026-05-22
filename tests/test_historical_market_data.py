from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from crypto_narrative_radar.data.historical import (
    HISTORICAL_OUTPUT_COLUMNS,
    add_calendar_lag_returns,
    build_failure_row,
    data_quality_flag,
    normalize_market_chart_response,
)


def _ts(date_text: str, hour: int = 0) -> int:
    dt = datetime.fromisoformat(f"{date_text}T{hour:02d}:00:00+00:00")
    return int(dt.timestamp() * 1000)


def _taxonomy_row() -> dict[str, object]:
    return {
        "coingecko_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "primary_narrative": "Layer 1",
        "secondary_narratives": "Store of value",
        "include_in_score": "TRUE",
    }


def test_normalization_converts_market_chart_arrays_to_expected_columns() -> None:
    response = {
        "prices": [[_ts("2026-01-01"), 100.0]],
        "market_caps": [[_ts("2026-01-01"), 1_000.0]],
        "total_volumes": [[_ts("2026-01-01"), 100.0]],
    }

    normalized = normalize_market_chart_response(
        "bitcoin", response, _taxonomy_row(), 90, "daily", "2026-05-22T00:00:00+00:00"
    )

    assert list(normalized.columns) == HISTORICAL_OUTPUT_COLUMNS
    assert normalized.loc[0, "date"] == "2026-01-01"
    assert normalized.loc[0, "coingecko_id"] == "bitcoin"
    assert normalized.loc[0, "symbol"] == "BTC"
    assert normalized.loc[0, "price_usd"] == 100.0
    assert normalized.loc[0, "volume_to_market_cap"] == 0.1


def test_daily_normalization_keeps_one_row_per_token_date() -> None:
    response = {
        "prices": [[_ts("2026-01-01", 1), 100.0], [_ts("2026-01-01", 23), 110.0]],
        "market_caps": [[_ts("2026-01-01", 1), 1_000.0], [_ts("2026-01-01", 23), 1_100.0]],
        "total_volumes": [[_ts("2026-01-01", 1), 100.0], [_ts("2026-01-01", 23), 120.0]],
    }

    normalized = normalize_market_chart_response(
        "bitcoin", response, _taxonomy_row(), 90, "daily", "2026-05-22T00:00:00+00:00"
    )

    assert len(normalized) == 1
    assert normalized.loc[0, "timestamp_ms"] == _ts("2026-01-01", 23)
    assert normalized.loc[0, "price_usd"] == 110.0


def test_calendar_lag_returns_are_calculated_when_exact_dates_exist() -> None:
    df = pd.DataFrame(
        [
            {"coingecko_id": "bitcoin", "date": "2026-01-01", "price_usd": 100.0},
            {"coingecko_id": "bitcoin", "date": "2026-01-02", "price_usd": 110.0},
            {"coingecko_id": "bitcoin", "date": "2026-01-08", "price_usd": 140.0},
            {"coingecko_id": "bitcoin", "date": "2026-01-31", "price_usd": 200.0},
        ]
    )

    with_returns = add_calendar_lag_returns(df)

    jan_02 = with_returns[with_returns["date"] == "2026-01-02"].iloc[0]
    jan_08 = with_returns[with_returns["date"] == "2026-01-08"].iloc[0]
    jan_31 = with_returns[with_returns["date"] == "2026-01-31"].iloc[0]

    assert jan_02["return_1d"] == pytest.approx(0.1)
    assert jan_08["return_7d"] == pytest.approx(0.4)
    assert jan_31["return_30d"] == pytest.approx(1.0)


def test_calendar_lag_returns_are_null_when_exact_lag_date_is_missing() -> None:
    df = pd.DataFrame(
        [
            {"coingecko_id": "bitcoin", "date": "2026-01-01", "price_usd": 100.0},
            {"coingecko_id": "bitcoin", "date": "2026-01-03", "price_usd": 130.0},
        ]
    )

    with_returns = add_calendar_lag_returns(df)
    jan_03 = with_returns[with_returns["date"] == "2026-01-03"].iloc[0]

    assert pd.isna(jan_03["return_1d"])


def test_return_calculation_does_not_use_simple_row_shift() -> None:
    df = pd.DataFrame(
        [
            {"coingecko_id": "bitcoin", "date": "2026-01-01", "price_usd": 100.0},
            {"coingecko_id": "bitcoin", "date": "2026-01-08", "price_usd": 120.0},
        ]
    )

    with_returns = add_calendar_lag_returns(df)
    jan_08 = with_returns[with_returns["date"] == "2026-01-08"].iloc[0]

    assert pd.isna(jan_08["return_1d"])
    assert jan_08["return_7d"] == pytest.approx(0.2)


def test_volume_to_market_cap_handles_zero_market_cap_safely() -> None:
    response = {
        "prices": [[_ts("2026-01-01"), 100.0]],
        "market_caps": [[_ts("2026-01-01"), 0.0]],
        "total_volumes": [[_ts("2026-01-01"), 100.0]],
    }

    normalized = normalize_market_chart_response(
        "bitcoin", response, _taxonomy_row(), 90, "daily", "2026-05-22T00:00:00+00:00"
    )

    assert pd.isna(normalized.loc[0, "volume_to_market_cap"])


def test_data_quality_flag_returns_ok_for_complete_rows() -> None:
    row = pd.Series(
        {
            "price_usd": 100.0,
            "market_cap_usd": 1_000.0,
            "total_volume_usd": 100.0,
            "return_1d": 0.01,
            "return_7d": 0.07,
            "return_30d": 0.3,
        }
    )

    assert data_quality_flag(row) == "ok"


def test_data_quality_flag_catches_missing_price() -> None:
    row = pd.Series({"price_usd": pd.NA})

    assert data_quality_flag(row) == "missing_price"


def test_data_quality_flag_catches_zero_or_negative_price() -> None:
    row = pd.Series({"price_usd": 0})

    assert data_quality_flag(row) == "zero_or_negative_price"


def test_failure_log_rows_can_be_built_without_stopping_pipeline() -> None:
    failure = build_failure_row(
        token=_taxonomy_row(),
        error_type="http_error",
        status_code=404,
        message="not found",
        attempted_at_utc="2026-05-22T00:00:00+00:00",
        attempt_count=1,
    )

    assert failure["coingecko_id"] == "bitcoin"
    assert failure["error_type"] == "http_error"
    assert failure["status_code"] == 404
