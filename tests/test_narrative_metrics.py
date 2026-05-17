import pandas as pd

from crypto_narrative_radar.metrics.narrative_metrics import (
    add_narrative_scores,
    calculate_narrative_metrics,
    create_narrative_ranking,
    safe_divide,
)


def sample_snapshot() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "coingecko_id": "bitcoin",
                "name": "Bitcoin",
                "primary_narrative": "Layer 1",
                "market_cap": 1000,
                "total_volume": 100,
                "price_change_percentage_24h": 1,
                "price_change_percentage_7d_in_currency": 10,
                "price_change_percentage_30d_in_currency": 20,
            },
            {
                "coingecko_id": "ethereum",
                "name": "Ethereum",
                "primary_narrative": "Layer 1",
                "market_cap": 500,
                "total_volume": 100,
                "price_change_percentage_24h": -1,
                "price_change_percentage_7d_in_currency": 6,
                "price_change_percentage_30d_in_currency": 12,
            },
            {
                "coingecko_id": "uniswap",
                "name": "Uniswap",
                "primary_narrative": "DeFi",
                "market_cap": 100,
                "total_volume": 20,
                "price_change_percentage_24h": 2,
                "price_change_percentage_7d_in_currency": 8,
                "price_change_percentage_30d_in_currency": -5,
            },
            {
                "coingecko_id": "aave",
                "name": "Aave",
                "primary_narrative": "DeFi",
                "market_cap": 100,
                "total_volume": 0,
                "price_change_percentage_24h": 3,
                "price_change_percentage_7d_in_currency": -2,
                "price_change_percentage_30d_in_currency": 5,
            },
        ]
    )


def test_aggregation_correctness() -> None:
    metrics = calculate_narrative_metrics(sample_snapshot())
    defi = metrics.loc[metrics["primary_narrative"] == "DeFi"].iloc[0]

    assert defi["token_count"] == 2
    assert defi["avg_return_7d"] == 3
    assert defi["median_return_7d"] == 3
    assert defi["total_market_cap"] == 200
    assert defi["total_volume"] == 20


def test_breadth_calculation() -> None:
    metrics = calculate_narrative_metrics(sample_snapshot())
    layer_1 = metrics.loc[metrics["primary_narrative"] == "Layer 1"].iloc[0]
    defi = metrics.loc[metrics["primary_narrative"] == "DeFi"].iloc[0]

    assert layer_1["breadth_24h"] == 0.5
    assert layer_1["breadth_7d"] == 1.0
    assert defi["breadth_7d"] == 0.5


def test_safe_volume_to_market_cap_division() -> None:
    result = safe_divide(
        pd.Series([10, 5]),
        pd.Series([100, 0]),
    )

    assert result.iloc[0] == 0.1
    assert pd.isna(result.iloc[1])


def test_relative_strength_calculation() -> None:
    metrics = calculate_narrative_metrics(sample_snapshot())
    defi = metrics.loc[metrics["primary_narrative"] == "DeFi"].iloc[0]

    assert defi["rs_vs_btc_7d"] == -7
    assert defi["rs_vs_eth_7d"] == -3
    assert defi["relative_strength_7d"] == -5


def test_score_range_between_zero_and_100() -> None:
    metrics = calculate_narrative_metrics(sample_snapshot())
    scored = add_narrative_scores(metrics)

    assert scored["narrative_momentum_score"].between(0, 100).all()
    assert scored["price_momentum_score"].between(0, 100).all()
    assert scored["volume_confirmation_score"].between(0, 100).all()
    assert scored["breadth_score"].between(0, 100).all()
    assert scored["relative_strength_score"].between(0, 100).all()


def test_final_score_uses_project_framework_weights() -> None:
    metrics = calculate_narrative_metrics(sample_snapshot())
    scored = add_narrative_scores(metrics)
    first = scored.iloc[0]

    expected_score = (
        0.40 * first["price_momentum_score"]
        + 0.25 * first["relative_strength_score"]
        + 0.20 * first["volume_confirmation_score"]
        + 0.15 * first["breadth_score"]
    )

    assert first["narrative_momentum_score"] == expected_score
    assert first["scoring_note"] == "Full V1 scoring weights applied."


def test_score_reweights_available_components_when_relative_strength_missing() -> None:
    snapshot = sample_snapshot()
    snapshot = snapshot[~snapshot["coingecko_id"].isin(["bitcoin", "ethereum"])]

    metrics = calculate_narrative_metrics(snapshot)
    scored = add_narrative_scores(metrics)
    first = scored.iloc[0]
    available_weight = 0.40 + 0.20 + 0.15
    expected_score = (
        0.40 * first["price_momentum_score"]
        + 0.20 * first["volume_confirmation_score"]
        + 0.15 * first["breadth_score"]
    ) / available_weight

    assert pd.isna(first["relative_strength_score"])
    assert first["narrative_momentum_score"] == expected_score
    assert "relative_strength" in first["scoring_note"]


def test_ranking_order() -> None:
    metrics = calculate_narrative_metrics(sample_snapshot())
    ranking = create_narrative_ranking(metrics)

    assert ranking["rank"].tolist() == [1, 2]
    assert ranking["narrative_momentum_score"].is_monotonic_decreasing
