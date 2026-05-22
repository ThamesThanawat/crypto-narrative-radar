"""Historical narrative-level market metrics."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from crypto_narrative_radar.config import PROCESSED_DATA_DIR
from crypto_narrative_radar.metrics.narrative_metrics import safe_divide


HISTORICAL_TOKEN_FILENAME = "token_market_history_90d.csv"
HISTORICAL_NARRATIVE_FILENAME = "narrative_market_history_90d.csv"
RETURN_WINDOWS = [1, 7, 30]
HISTORICAL_NARRATIVE_COLUMNS = [
    "date",
    "primary_narrative",
    "token_count",
    "valid_price_token_count",
    "ok_token_count",
    "avg_return_1d",
    "median_return_1d",
    "avg_return_7d",
    "median_return_7d",
    "avg_return_30d",
    "median_return_30d",
    "total_market_cap_usd",
    "total_volume_usd",
    "avg_volume_to_market_cap",
    "breadth_1d",
    "breadth_7d",
    "breadth_30d",
    "return_1d_valid_count",
    "return_7d_valid_count",
    "return_30d_valid_count",
    "top_token_by_market_cap",
    "top_token_market_cap_usd",
    "top_token_market_cap_share",
    "concentration_flag",
    "btc_return_1d",
    "btc_return_7d",
    "btc_return_30d",
    "eth_return_1d",
    "eth_return_7d",
    "eth_return_30d",
    "rs_vs_btc_1d",
    "rs_vs_btc_7d",
    "rs_vs_btc_30d",
    "rs_vs_eth_1d",
    "rs_vs_eth_7d",
    "rs_vs_eth_30d",
    "relative_strength_1d",
    "relative_strength_7d",
    "relative_strength_30d",
]


def historical_token_path(
    input_name: str = HISTORICAL_TOKEN_FILENAME,
    base_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Return the processed historical token market data path."""
    return base_dir / "historical" / input_name


def historical_narrative_path(
    output_name: str = HISTORICAL_NARRATIVE_FILENAME,
    base_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Return the processed historical narrative metrics path."""
    return base_dir / "historical" / output_name


def load_historical_token_data(path: Path) -> pd.DataFrame:
    """Load a historical token market data CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Historical token market data not found: {path}")
    return pd.read_csv(path)


def _positive_share_valid(series: pd.Series) -> float | pd.NA:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return pd.NA
    return float((numeric > 0).sum() / len(numeric))


def _valid_count(series: pd.Series) -> int:
    return int(pd.to_numeric(series, errors="coerce").notna().sum())


def _concentration_flag(top_token_share: object) -> str:
    if pd.isna(top_token_share):
        return "Unknown"
    if top_token_share < 0.30:
        return "Low"
    if top_token_share <= 0.50:
        return "Medium"
    return "High"


def _top_token_rows(history_df: pd.DataFrame) -> pd.DataFrame:
    sorted_tokens = history_df.sort_values(
        ["date", "primary_narrative", "market_cap_usd"],
        ascending=[True, True, False],
        na_position="last",
    )
    top_tokens = sorted_tokens.drop_duplicates(["date", "primary_narrative"])
    return top_tokens[
        ["date", "primary_narrative", "name", "market_cap_usd"]
    ].rename(
        columns={
            "name": "top_token_by_market_cap",
            "market_cap_usd": "top_token_market_cap_usd",
        }
    )


def _benchmark_returns(history_df: pd.DataFrame, coingecko_id: str, prefix: str) -> pd.DataFrame:
    benchmark = history_df.loc[history_df["coingecko_id"] == coingecko_id].copy()
    columns = ["date"] + [f"return_{days}d" for days in RETURN_WINDOWS]
    benchmark = benchmark[columns].drop_duplicates("date")
    return benchmark.rename(
        columns={f"return_{days}d": f"{prefix}_return_{days}d" for days in RETURN_WINDOWS}
    )


def calculate_historical_narrative_metrics(history_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate token-level history into daily narrative-level metrics."""
    required_columns = [
        "date",
        "coingecko_id",
        "name",
        "primary_narrative",
        "price_usd",
        "market_cap_usd",
        "total_volume_usd",
        "volume_to_market_cap",
        "return_1d",
        "return_7d",
        "return_30d",
        "data_quality_flag",
    ]
    missing_columns = [column for column in required_columns if column not in history_df]
    if missing_columns:
        raise ValueError(
            "Historical token market data missing columns: "
            + ", ".join(missing_columns)
        )
    if history_df.empty:
        raise ValueError("Historical token market data is empty.")

    working_df = history_df.copy()
    for column in [
        "price_usd",
        "market_cap_usd",
        "total_volume_usd",
        "volume_to_market_cap",
        "return_1d",
        "return_7d",
        "return_30d",
    ]:
        working_df[column] = pd.to_numeric(working_df[column], errors="coerce")

    grouped = working_df.groupby(["date", "primary_narrative"], dropna=False)
    metrics = grouped.agg(
        token_count=("coingecko_id", "nunique"),
        valid_price_token_count=("price_usd", _valid_count),
        ok_token_count=("data_quality_flag", lambda series: int((series == "ok").sum())),
        avg_return_1d=("return_1d", "mean"),
        median_return_1d=("return_1d", "median"),
        avg_return_7d=("return_7d", "mean"),
        median_return_7d=("return_7d", "median"),
        avg_return_30d=("return_30d", "mean"),
        median_return_30d=("return_30d", "median"),
        total_market_cap_usd=("market_cap_usd", "sum"),
        total_volume_usd=("total_volume_usd", "sum"),
        avg_volume_to_market_cap=("volume_to_market_cap", "mean"),
    ).reset_index()

    breadth = grouped.agg(
        breadth_1d=("return_1d", _positive_share_valid),
        breadth_7d=("return_7d", _positive_share_valid),
        breadth_30d=("return_30d", _positive_share_valid),
        return_1d_valid_count=("return_1d", _valid_count),
        return_7d_valid_count=("return_7d", _valid_count),
        return_30d_valid_count=("return_30d", _valid_count),
    ).reset_index()
    metrics = metrics.merge(breadth, on=["date", "primary_narrative"], how="left")

    top_tokens = _top_token_rows(working_df)
    metrics = metrics.merge(top_tokens, on=["date", "primary_narrative"], how="left")
    metrics["top_token_market_cap_share"] = safe_divide(
        metrics["top_token_market_cap_usd"],
        metrics["total_market_cap_usd"],
    )
    metrics["concentration_flag"] = metrics["top_token_market_cap_share"].apply(
        _concentration_flag
    )

    metrics = metrics.merge(
        _benchmark_returns(working_df, "bitcoin", "btc"),
        on="date",
        how="left",
    )
    metrics = metrics.merge(
        _benchmark_returns(working_df, "ethereum", "eth"),
        on="date",
        how="left",
    )

    for days in RETURN_WINDOWS:
        median_column = f"median_return_{days}d"
        metrics[f"rs_vs_btc_{days}d"] = (
            metrics[median_column] - metrics[f"btc_return_{days}d"]
        )
        metrics[f"rs_vs_eth_{days}d"] = (
            metrics[median_column] - metrics[f"eth_return_{days}d"]
        )
        metrics[f"relative_strength_{days}d"] = metrics[
            [f"rs_vs_btc_{days}d", f"rs_vs_eth_{days}d"]
        ].mean(axis=1, skipna=True)

    return metrics[HISTORICAL_NARRATIVE_COLUMNS].replace(
        [float("inf"), float("-inf")],
        pd.NA,
    ).sort_values(["date", "primary_narrative"]).reset_index(drop=True)


def save_historical_narrative_metrics(
    metrics_df: pd.DataFrame,
    output_name: str = HISTORICAL_NARRATIVE_FILENAME,
    base_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Save historical narrative metrics to the processed historical folder."""
    output_path = historical_narrative_path(output_name, base_dir=base_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(output_path, index=False)
    return output_path


def build_historical_narrative_metrics(
    input_name: str = HISTORICAL_TOKEN_FILENAME,
    output_name: str = HISTORICAL_NARRATIVE_FILENAME,
    base_dir: Path = PROCESSED_DATA_DIR,
) -> tuple[pd.DataFrame, Path]:
    """Build and save daily historical narrative metrics."""
    input_path = historical_token_path(input_name, base_dir=base_dir)
    history_df = load_historical_token_data(input_path)
    metrics_df = calculate_historical_narrative_metrics(history_df)
    output_path = save_historical_narrative_metrics(
        metrics_df,
        output_name=output_name,
        base_dir=base_dir,
    )
    return metrics_df, output_path
