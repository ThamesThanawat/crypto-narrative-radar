import pandas as pd
import pytest

from crypto_narrative_radar.metrics.historical_narrative_metrics import (
    HISTORICAL_NARRATIVE_COLUMNS,
    calculate_historical_narrative_metrics,
)


def sample_history() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "date": "2026-01-01",
                "coingecko_id": "bitcoin",
                "name": "Bitcoin",
                "primary_narrative": "Layer 1",
                "price_usd": 100,
                "market_cap_usd": 1000,
                "total_volume_usd": 100,
                "volume_to_market_cap": 0.10,
                "return_1d": 0.10,
                "return_7d": 0.20,
                "return_30d": 0.30,
                "data_quality_flag": "ok",
            },
            {
                "date": "2026-01-01",
                "coingecko_id": "ethereum",
                "name": "Ethereum",
                "primary_narrative": "Layer 1",
                "price_usd": 50,
                "market_cap_usd": 500,
                "total_volume_usd": 50,
                "volume_to_market_cap": 0.10,
                "return_1d": 0.04,
                "return_7d": 0.10,
                "return_30d": 0.20,
                "data_quality_flag": "ok",
            },
            {
                "date": "2026-01-01",
                "coingecko_id": "uniswap",
                "name": "Uniswap",
                "primary_narrative": "DeFi",
                "price_usd": 10,
                "market_cap_usd": 100,
                "total_volume_usd": 25,
                "volume_to_market_cap": 0.25,
                "return_1d": 0.02,
                "return_7d": 0.08,
                "return_30d": -0.05,
                "data_quality_flag": "ok",
            },
            {
                "date": "2026-01-01",
                "coingecko_id": "aave",
                "name": "Aave",
                "primary_narrative": "DeFi",
                "price_usd": 5,
                "market_cap_usd": 100,
                "total_volume_usd": 5,
                "volume_to_market_cap": 0.05,
                "return_1d": -0.01,
                "return_7d": pd.NA,
                "return_30d": 0.05,
                "data_quality_flag": "incomplete_lag_history",
            },
        ]
    )


def test_historical_metrics_have_expected_columns() -> None:
    metrics = calculate_historical_narrative_metrics(sample_history())

    assert list(metrics.columns) == HISTORICAL_NARRATIVE_COLUMNS


def test_historical_metrics_aggregate_by_date_and_narrative() -> None:
    metrics = calculate_historical_narrative_metrics(sample_history())
    defi = metrics.loc[metrics["primary_narrative"] == "DeFi"].iloc[0]

    assert defi["token_count"] == 2
    assert defi["ok_token_count"] == 1
    assert defi["median_return_1d"] == pytest.approx(0.005)
    assert defi["median_return_7d"] == pytest.approx(0.08)
    assert defi["total_market_cap_usd"] == 200
    assert defi["total_volume_usd"] == 30
    assert defi["avg_volume_to_market_cap"] == pytest.approx(0.15)


def test_historical_breadth_uses_valid_return_observations() -> None:
    metrics = calculate_historical_narrative_metrics(sample_history())
    defi = metrics.loc[metrics["primary_narrative"] == "DeFi"].iloc[0]

    assert defi["breadth_1d"] == 0.5
    assert defi["breadth_7d"] == 1.0
    assert defi["return_7d_valid_count"] == 1


def test_historical_relative_strength_uses_daily_benchmarks() -> None:
    metrics = calculate_historical_narrative_metrics(sample_history())
    defi = metrics.loc[metrics["primary_narrative"] == "DeFi"].iloc[0]

    assert defi["btc_return_7d"] == 0.20
    assert defi["eth_return_7d"] == 0.10
    assert defi["rs_vs_btc_7d"] == pytest.approx(-0.12)
    assert defi["rs_vs_eth_7d"] == pytest.approx(-0.02)
    assert defi["relative_strength_7d"] == pytest.approx(-0.07)


def test_historical_top_token_and_concentration_are_daily() -> None:
    metrics = calculate_historical_narrative_metrics(sample_history())
    layer_1 = metrics.loc[metrics["primary_narrative"] == "Layer 1"].iloc[0]

    assert layer_1["top_token_by_market_cap"] == "Bitcoin"
    assert layer_1["top_token_market_cap_usd"] == 1000
    assert layer_1["top_token_market_cap_share"] == pytest.approx(1000 / 1500)
    assert layer_1["concentration_flag"] == "High"
