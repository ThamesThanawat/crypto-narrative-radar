"""Narrative-level metrics and research ranking."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from crypto_narrative_radar.config import PROCESSED_DATA_DIR


SNAPSHOT_FILENAME_TEMPLATE = "token_market_snapshot_{run_date}.csv"
NARRATIVE_METRICS_FILENAME = "narrative_metrics.csv"
NARRATIVE_RANKING_FILENAME = "narrative_ranking.csv"
RETURN_24H = "price_change_percentage_24h"
RETURN_7D = "price_change_percentage_7d_in_currency"
RETURN_30D = "price_change_percentage_30d_in_currency"
SCORE_WEIGHTS = {
    "price_momentum_score": 0.40,
    "relative_strength_score": 0.25,
    "volume_confirmation_score": 0.20,
    "breadth_score": 0.15,
}


def get_snapshot_path(
    run_date: date | str | None = None,
    base_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Return a dated token market snapshot path."""
    if run_date is None:
        run_date = find_latest_processed_date(base_dir)
    run_date_text = run_date.isoformat() if isinstance(run_date, date) else str(run_date)
    return base_dir / run_date_text / SNAPSHOT_FILENAME_TEMPLATE.format(
        run_date=run_date_text
    )


def find_latest_processed_date(base_dir: Path = PROCESSED_DATA_DIR) -> str:
    """Find the latest processed snapshot folder."""
    snapshot_paths = sorted(
        base_dir.glob("*/token_market_snapshot_*.csv"),
        key=lambda path: path.parent.name,
    )
    if not snapshot_paths:
        raise FileNotFoundError("No processed token market snapshot found.")
    return snapshot_paths[-1].parent.name


def load_market_snapshot(path: Path) -> pd.DataFrame:
    """Load a processed token market snapshot CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Market snapshot not found: {path}")
    return pd.read_csv(path)


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divide two series and return missing values for zero denominators."""
    numeric_denominator = pd.to_numeric(denominator, errors="coerce")
    numeric_numerator = pd.to_numeric(numerator, errors="coerce")
    result = numeric_numerator / numeric_denominator.where(numeric_denominator != 0)
    return result.replace([float("inf"), float("-inf")], pd.NA)


def _positive_share(series: pd.Series) -> float:
    numeric = pd.to_numeric(series, errors="coerce")
    if len(numeric) == 0:
        return 0.0
    return float((numeric > 0).sum() / len(numeric))


def _top_token_rows(snapshot_df: pd.DataFrame) -> pd.DataFrame:
    sorted_tokens = snapshot_df.sort_values(
        ["primary_narrative", "market_cap"],
        ascending=[True, False],
        na_position="last",
    )
    top_tokens = sorted_tokens.drop_duplicates("primary_narrative")
    return top_tokens[
        ["primary_narrative", "name", "market_cap"]
    ].rename(
        columns={
            "name": "top_token_by_market_cap",
            "market_cap": "top_token_market_cap",
        }
    )


def _concentration_flag(top_token_share: object) -> str:
    if pd.isna(top_token_share):
        return "Unknown"
    if top_token_share < 0.30:
        return "Low"
    if top_token_share <= 0.50:
        return "Medium"
    return "High"


def _benchmark_return(snapshot_df: pd.DataFrame, coingecko_id: str) -> float | None:
    matching = snapshot_df.loc[snapshot_df["coingecko_id"] == coingecko_id, RETURN_7D]
    if matching.empty or pd.isna(matching.iloc[0]):
        return None
    return float(matching.iloc[0])


def _percentile_score(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() == 0:
        return pd.Series(pd.NA, index=series.index, dtype="Float64")
    return numeric.rank(pct=True, method="average") * 100


def _available_score_components(row: pd.Series) -> list[str]:
    return [column for column in SCORE_WEIGHTS if pd.notna(row[column])]


def _weighted_score(row: pd.Series) -> float | pd.NA:
    weighted_sum = 0.0
    active_weight = 0.0
    for column in _available_score_components(row):
        value = row[column]
        weight = SCORE_WEIGHTS[column]
        if pd.notna(value):
            weighted_sum += float(value) * weight
            active_weight += weight
    if active_weight == 0:
        return pd.NA
    return weighted_sum / active_weight


def _scoring_note(row: pd.Series) -> str:
    available_components = _available_score_components(row)
    missing_components = [
        column.replace("_score", "")
        for column in SCORE_WEIGHTS
        if column not in available_components
    ]
    if not missing_components:
        return "Full V1 scoring weights applied."
    return (
        "Unavailable component(s) omitted and remaining weights reweighted "
        f"proportionally: {', '.join(missing_components)}."
    )


def calculate_narrative_metrics(snapshot_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate token market snapshots into narrative-level metrics."""
    required_columns = [
        "coingecko_id",
        "name",
        "primary_narrative",
        "market_cap",
        "total_volume",
        RETURN_24H,
        RETURN_7D,
        RETURN_30D,
    ]
    missing_columns = [
        column for column in required_columns if column not in snapshot_df.columns
    ]
    if missing_columns:
        raise ValueError(f"Market snapshot missing columns: {', '.join(missing_columns)}")
    if snapshot_df.empty:
        raise ValueError("Market snapshot is empty.")

    working_df = snapshot_df.copy()
    for column in ["market_cap", "total_volume", RETURN_24H, RETURN_7D, RETURN_30D]:
        working_df[column] = pd.to_numeric(working_df[column], errors="coerce")
    working_df["volume_to_market_cap"] = safe_divide(
        working_df["total_volume"],
        working_df["market_cap"],
    )

    grouped = working_df.groupby("primary_narrative", dropna=False)
    metrics = grouped.agg(
        token_count=("coingecko_id", "nunique"),
        avg_return_24h=(RETURN_24H, "mean"),
        median_return_24h=(RETURN_24H, "median"),
        avg_return_7d=(RETURN_7D, "mean"),
        median_return_7d=(RETURN_7D, "median"),
        avg_return_30d=(RETURN_30D, "mean"),
        median_return_30d=(RETURN_30D, "median"),
        total_market_cap=("market_cap", "sum"),
        total_volume=("total_volume", "sum"),
        avg_volume_to_market_cap=("volume_to_market_cap", "mean"),
    ).reset_index()

    breadth = grouped.agg(
        breadth_24h=(RETURN_24H, _positive_share),
        breadth_7d=(RETURN_7D, _positive_share),
        breadth_30d=(RETURN_30D, _positive_share),
    ).reset_index()
    metrics = metrics.merge(breadth, on="primary_narrative", how="left")

    top_tokens = _top_token_rows(working_df)
    metrics = metrics.merge(top_tokens, on="primary_narrative", how="left")
    metrics["top_token_market_cap_share"] = safe_divide(
        metrics["top_token_market_cap"],
        metrics["total_market_cap"],
    )
    metrics["concentration_flag"] = metrics["top_token_market_cap_share"].apply(
        _concentration_flag
    )

    btc_return_7d = _benchmark_return(working_df, "bitcoin")
    eth_return_7d = _benchmark_return(working_df, "ethereum")
    metrics["btc_return_7d"] = btc_return_7d
    metrics["eth_return_7d"] = eth_return_7d
    metrics["rs_vs_btc_7d"] = (
        metrics["median_return_7d"] - btc_return_7d
        if btc_return_7d is not None
        else pd.NA
    )
    metrics["rs_vs_eth_7d"] = (
        metrics["median_return_7d"] - eth_return_7d
        if eth_return_7d is not None
        else pd.NA
    )
    metrics["relative_strength_7d"] = metrics[
        ["rs_vs_btc_7d", "rs_vs_eth_7d"]
    ].mean(axis=1, skipna=True)

    return metrics.replace([float("inf"), float("-inf")], pd.NA)


def add_narrative_scores(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Add normalized component scores and the Narrative Momentum Score."""
    scored = metrics_df.copy()
    scored["price_momentum_raw"] = (
        0.20 * scored["median_return_24h"]
        + 0.50 * scored["median_return_7d"]
        + 0.30 * scored["median_return_30d"]
    )
    scored["volume_confirmation_raw"] = scored["avg_volume_to_market_cap"]
    scored["breadth_raw"] = (
        0.20 * scored["breadth_24h"]
        + 0.50 * scored["breadth_7d"]
        + 0.30 * scored["breadth_30d"]
    )
    scored["relative_strength_raw"] = scored["relative_strength_7d"]

    scored["price_momentum_score"] = _percentile_score(scored["price_momentum_raw"])
    scored["volume_confirmation_score"] = _percentile_score(
        scored["volume_confirmation_raw"]
    )
    scored["breadth_score"] = _percentile_score(scored["breadth_raw"])
    scored["relative_strength_score"] = _percentile_score(
        scored["relative_strength_raw"]
    )
    scored["narrative_momentum_score"] = scored.apply(_weighted_score, axis=1)
    scored["scoring_note"] = scored.apply(_scoring_note, axis=1)

    return scored.replace([float("inf"), float("-inf")], pd.NA)


def create_narrative_ranking(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Create a descending narrative research ranking."""
    ranking = add_narrative_scores(metrics_df).sort_values(
        ["narrative_momentum_score", "primary_narrative"],
        ascending=[False, True],
        na_position="last",
    )
    ranking.insert(0, "rank", range(1, len(ranking) + 1))
    return ranking.reset_index(drop=True)


def save_narrative_metrics(
    metrics_df: pd.DataFrame,
    run_date: date | str,
    base_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Save narrative metrics to the processed date folder."""
    run_date_text = run_date.isoformat() if isinstance(run_date, date) else str(run_date)
    output_dir = base_dir / run_date_text
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / NARRATIVE_METRICS_FILENAME
    metrics_df.to_csv(output_path, index=False)
    return output_path


def save_narrative_ranking(
    ranking_df: pd.DataFrame,
    run_date: date | str,
    base_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Save narrative ranking to the processed date folder."""
    run_date_text = run_date.isoformat() if isinstance(run_date, date) else str(run_date)
    output_dir = base_dir / run_date_text
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / NARRATIVE_RANKING_FILENAME
    ranking_df.to_csv(output_path, index=False)
    return output_path


def build_narrative_outputs(
    run_date: date | str | None = None,
    base_dir: Path = PROCESSED_DATA_DIR,
) -> tuple[pd.DataFrame, pd.DataFrame, Path, Path]:
    """Build and save narrative metrics plus ranking for a processed snapshot."""
    if run_date is None:
        run_date = find_latest_processed_date(base_dir)
    snapshot_path = get_snapshot_path(run_date, base_dir)
    snapshot_df = load_market_snapshot(snapshot_path)
    metrics_df = calculate_narrative_metrics(snapshot_df)
    ranking_df = create_narrative_ranking(metrics_df)
    metrics_path = save_narrative_metrics(metrics_df, run_date, base_dir)
    ranking_path = save_narrative_ranking(ranking_df, run_date, base_dir)
    return metrics_df, ranking_df, metrics_path, ranking_path
