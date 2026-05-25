"""Narrative watchlist indicators for historical research screening."""

from __future__ import annotations

import pandas as pd


WATCHLIST_OUTPUT_FILENAME = "narrative_watchlist_indicators_90d.csv"
WATCHLIST_REQUIRED_COLUMNS = [
    "date",
    "primary_narrative",
    "median_return_7d",
    "median_return_30d",
    "breadth_7d",
    "avg_volume_to_market_cap",
    "rs_vs_btc_7d",
]
WATCH_FLAG_COLUMNS = [
    "watch_volume_accel",
    "watch_breadth_expand",
    "watch_quiet_rs",
    "watch_momentum_pickup",
]
WATCHLIST_LABELS = {
    0: "No Watch",
    1: "Low Research Interest",
    2: "Monitor",
    3: "Review Closely",
    4: "High Research Interest",
}


def _validate_columns(df: pd.DataFrame) -> None:
    missing_columns = [
        column for column in WATCHLIST_REQUIRED_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            "Historical narrative metrics missing columns: "
            + ", ".join(missing_columns)
        )


def _recent_and_prior_7d_means(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    numeric = pd.to_numeric(series, errors="coerce")
    recent_mean = numeric.rolling(window=7, min_periods=7).mean()
    prior_mean = recent_mean.shift(7)
    return recent_mean, prior_mean


def _rolling_flags_for_narrative(group: pd.DataFrame) -> pd.DataFrame:
    sorted_group = group.copy()
    sorted_group["_parsed_date"] = pd.to_datetime(sorted_group["date"], errors="coerce")
    sorted_group = sorted_group.sort_values(
        ["_parsed_date", "date"],
        kind="mergesort",
        na_position="last",
    )

    recent_volume, prior_volume = _recent_and_prior_7d_means(
        sorted_group["avg_volume_to_market_cap"]
    )
    valid_volume = prior_volume.notna() & (prior_volume != 0) & recent_volume.notna()
    sorted_group["watch_volume_accel"] = (
        valid_volume & ((recent_volume / prior_volume) > 1.15)
    )

    recent_breadth, prior_breadth = _recent_and_prior_7d_means(
        sorted_group["breadth_7d"]
    )
    valid_breadth = prior_breadth.notna() & recent_breadth.notna()
    sorted_group["watch_breadth_expand"] = (
        valid_breadth & (recent_breadth > (prior_breadth + 0.05))
    )

    return sorted_group.drop(columns=["_parsed_date"])


def calculate_watchlist_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add narrative watchlist indicators to historical narrative metrics."""
    _validate_columns(df)
    if df.empty:
        result = df.copy()
        for column in WATCH_FLAG_COLUMNS:
            result[column] = pd.Series(dtype=bool)
        result["watchlist_score"] = pd.Series(dtype="int64")
        result["watchlist_label"] = pd.Series(dtype=object)
        return result

    working_df = df.copy()
    working_df["_original_order"] = range(len(working_df))

    rolling_groups = [
        _rolling_flags_for_narrative(group)
        for _, group in working_df.groupby("primary_narrative", dropna=False)
    ]
    rolling_flags = pd.concat(rolling_groups, ignore_index=True)

    median_return_7d = pd.to_numeric(
        rolling_flags["median_return_7d"],
        errors="coerce",
    )
    median_return_30d = pd.to_numeric(
        rolling_flags["median_return_30d"],
        errors="coerce",
    )
    rs_vs_btc_7d = pd.to_numeric(rolling_flags["rs_vs_btc_7d"], errors="coerce")

    rolling_flags["watch_quiet_rs"] = (
        rs_vs_btc_7d.notna()
        & median_return_7d.notna()
        & (rs_vs_btc_7d > 0)
        & (median_return_7d < 0.10)
    )
    rolling_flags["watch_momentum_pickup"] = (
        median_return_7d.notna()
        & median_return_30d.notna()
        & (median_return_7d > median_return_30d)
    )

    for column in WATCH_FLAG_COLUMNS:
        rolling_flags[column] = rolling_flags[column].fillna(False).astype(bool)

    rolling_flags["watchlist_score"] = (
        rolling_flags[WATCH_FLAG_COLUMNS].sum(axis=1).astype(int)
    )
    rolling_flags["watchlist_label"] = rolling_flags["watchlist_score"].map(
        WATCHLIST_LABELS
    )

    return (
        rolling_flags.sort_values("_original_order")
        .drop(columns=["_original_order"])
        .reset_index(drop=True)
    )
