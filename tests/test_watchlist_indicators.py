import pandas as pd

from crypto_narrative_radar.metrics.watchlist_indicators import (
    WATCH_FLAG_COLUMNS,
    calculate_watchlist_indicators,
)


def make_rows(
    narrative: str = "AI",
    periods: int = 14,
    prior_volume: float = 0.10,
    recent_volume: float = 0.12,
    prior_breadth: float = 0.50,
    recent_breadth: float = 0.56,
    median_return_7d: float = 0.05,
    median_return_30d: float = 0.02,
    rs_vs_btc_7d: float = 0.02,
) -> list[dict[str, object]]:
    dates = pd.date_range("2026-01-01", periods=periods, freq="D")
    rows: list[dict[str, object]] = []
    for index, date_value in enumerate(dates):
        is_recent = index >= 7
        rows.append(
            {
                "date": date_value.date().isoformat(),
                "primary_narrative": narrative,
                "median_return_7d": median_return_7d,
                "median_return_30d": median_return_30d,
                "breadth_7d": recent_breadth if is_recent else prior_breadth,
                "avg_volume_to_market_cap": recent_volume if is_recent else prior_volume,
                "rs_vs_btc_7d": rs_vs_btc_7d,
                "rs_vs_eth_7d": rs_vs_btc_7d + 0.01,
            }
        )
    return rows


def test_all_watch_flags_false_when_data_is_all_nan() -> None:
    df = pd.DataFrame(make_rows())
    for column in [
        "median_return_7d",
        "median_return_30d",
        "breadth_7d",
        "avg_volume_to_market_cap",
        "rs_vs_btc_7d",
    ]:
        df[column] = pd.NA

    result = calculate_watchlist_indicators(df)
    last = result.iloc[-1]

    assert not last[WATCH_FLAG_COLUMNS].any()
    assert last["watchlist_score"] == 0
    assert last["watchlist_label"] == "No Watch"


def test_all_four_watch_flags_true_when_conditions_are_met() -> None:
    result = calculate_watchlist_indicators(pd.DataFrame(make_rows()))
    last = result.iloc[-1]

    assert last["watch_volume_accel"]
    assert last["watch_breadth_expand"]
    assert last["watch_quiet_rs"]
    assert last["watch_momentum_pickup"]
    assert last["watchlist_score"] == 4
    assert last["watchlist_label"] == "High Research Interest"


def test_watch_quiet_rs_condition() -> None:
    true_row = pd.DataFrame(make_rows(rs_vs_btc_7d=0.02, median_return_7d=0.05))
    false_row = pd.DataFrame(make_rows(rs_vs_btc_7d=0.02, median_return_7d=0.15))

    assert calculate_watchlist_indicators(true_row).iloc[-1]["watch_quiet_rs"]
    assert not calculate_watchlist_indicators(false_row).iloc[-1]["watch_quiet_rs"]


def test_watch_momentum_pickup_condition() -> None:
    true_row = pd.DataFrame(
        make_rows(median_return_7d=0.05, median_return_30d=0.02)
    )
    false_row = pd.DataFrame(
        make_rows(median_return_7d=0.02, median_return_30d=0.05)
    )

    assert calculate_watchlist_indicators(true_row).iloc[-1]["watch_momentum_pickup"]
    assert not calculate_watchlist_indicators(false_row).iloc[-1][
        "watch_momentum_pickup"
    ]


def test_watch_volume_accel_true_when_recent_mean_is_more_than_15_percent_higher() -> None:
    true_df = pd.DataFrame(make_rows(prior_volume=0.10, recent_volume=0.12))
    flat_df = pd.DataFrame(make_rows(prior_volume=0.10, recent_volume=0.10))

    assert calculate_watchlist_indicators(true_df).iloc[-1]["watch_volume_accel"]
    assert not calculate_watchlist_indicators(flat_df).iloc[-1]["watch_volume_accel"]


def test_watch_breadth_expand_true_only_above_five_point_improvement() -> None:
    true_df = pd.DataFrame(make_rows(prior_breadth=0.50, recent_breadth=0.56))
    small_move_df = pd.DataFrame(make_rows(prior_breadth=0.50, recent_breadth=0.53))

    assert calculate_watchlist_indicators(true_df).iloc[-1]["watch_breadth_expand"]
    assert not calculate_watchlist_indicators(small_move_df).iloc[-1][
        "watch_breadth_expand"
    ]


def test_nan_handling_does_not_crash() -> None:
    df = pd.DataFrame(make_rows())
    df.loc[13, "avg_volume_to_market_cap"] = pd.NA
    df.loc[13, "breadth_7d"] = pd.NA
    df.loc[13, "rs_vs_btc_7d"] = pd.NA

    result = calculate_watchlist_indicators(df)

    assert len(result) == len(df)
    assert result[WATCH_FLAG_COLUMNS].dtypes.apply(lambda dtype: dtype == bool).all()


def test_narratives_are_not_mixed_in_rolling_calculations() -> None:
    ai_rows = make_rows(
        narrative="AI",
        prior_volume=0.10,
        recent_volume=0.12,
        prior_breadth=0.50,
        recent_breadth=0.56,
    )
    defi_rows = make_rows(
        narrative="DeFi",
        prior_volume=0.10,
        recent_volume=0.10,
        prior_breadth=0.50,
        recent_breadth=0.50,
    )
    mixed_df = pd.DataFrame(ai_rows + defi_rows).sort_values(
        ["date", "primary_narrative"]
    )

    result = calculate_watchlist_indicators(mixed_df)
    latest = result.groupby("primary_narrative").tail(1).set_index("primary_narrative")

    assert latest.loc["AI", "watch_volume_accel"]
    assert latest.loc["AI", "watch_breadth_expand"]
    assert not latest.loc["DeFi", "watch_volume_accel"]
    assert not latest.loc["DeFi", "watch_breadth_expand"]


def test_score_and_label_mapping_are_correct() -> None:
    no_watch = pd.DataFrame(
        make_rows(
            prior_volume=0.10,
            recent_volume=0.10,
            prior_breadth=0.50,
            recent_breadth=0.50,
            median_return_7d=0.15,
            median_return_30d=0.20,
            rs_vs_btc_7d=-0.01,
        )
    )
    one_watch = pd.DataFrame(
        make_rows(
            prior_volume=0.10,
            recent_volume=0.10,
            prior_breadth=0.50,
            recent_breadth=0.50,
            median_return_7d=0.05,
            median_return_30d=0.02,
            rs_vs_btc_7d=-0.01,
        )
    )
    two_watch = pd.DataFrame(
        make_rows(
            prior_volume=0.10,
            recent_volume=0.10,
            prior_breadth=0.50,
            recent_breadth=0.50,
            median_return_7d=0.05,
            median_return_30d=0.02,
            rs_vs_btc_7d=0.02,
        )
    )
    three_watch = pd.DataFrame(
        make_rows(
            prior_volume=0.10,
            recent_volume=0.12,
            prior_breadth=0.50,
            recent_breadth=0.50,
            median_return_7d=0.05,
            median_return_30d=0.02,
            rs_vs_btc_7d=0.02,
        )
    )
    four_watch = pd.DataFrame(make_rows())

    cases = [
        (no_watch, 0, "No Watch"),
        (one_watch, 1, "Low Research Interest"),
        (two_watch, 2, "Monitor"),
        (three_watch, 3, "Review Closely"),
        (four_watch, 4, "High Research Interest"),
    ]
    for frame, expected_score, expected_label in cases:
        last = calculate_watchlist_indicators(frame).iloc[-1]
        assert last["watchlist_score"] == expected_score
        assert last["watchlist_label"] == expected_label
