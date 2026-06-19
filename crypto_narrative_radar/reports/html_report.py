"""Static HTML research report generation."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from crypto_narrative_radar.config import (
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
    REPORTS_DIR,
    TEMPLATES_DIR,
)


DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REPORT_FILENAME_TEMPLATE = "crypto_narrative_report_{snapshot_date}.html"
SAMPLE_REPORT_DATE = "2026-05-20"
SAMPLE_REPORT_FILENAME_TEMPLATE = "sample_{snapshot_date}.html"
SHOWCASE_DIR = PROJECT_ROOT / "docs" / "showcase"
TOKEN_SNAPSHOT_TEMPLATE = "token_market_snapshot_{snapshot_date}.csv"
TEMPLATE_NAME = "research_report.html.j2"
STALE_MARKET_DATA_DAYS = 2
SAMPLE_REPORT_NOTE = (
    "Pinned sample report: this report uses the fixed 2026-05-20 snapshot "
    "to demonstrate narrative scoring, data quality notes, component "
    "breakdown, and return skew diagnostics. It is intended as a "
    "reproducible methodology example, not a current market update."
)
CURRENT_RETURN_COLUMNS = (
    "price_change_percentage_24h",
    "price_change_percentage_7d_in_currency",
    "price_change_percentage_30d_in_currency",
)
CURRENT_NARRATIVE_RETURN_COLUMNS = (
    "avg_return_24h",
    "median_return_24h",
    "avg_return_7d",
    "median_return_7d",
    "avg_return_30d",
    "median_return_30d",
    "relative_strength_7d",
    "rs_vs_btc_7d",
    "rs_vs_eth_7d",
)
HISTORICAL_RATIO_PERCENT_COLUMNS = {
    "avg_return_1d",
    "median_return_1d",
    "avg_return_7d",
    "median_return_7d",
    "avg_return_30d",
    "median_return_30d",
    "breadth_1d",
    "breadth_7d",
    "breadth_30d",
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
}
PERCENT_POINT_COLUMNS = {
    "avg_return_24h",
    "median_return_24h",
    "avg_return_7d",
    "median_return_7d",
    "avg_return_30d",
    "median_return_30d",
    "avg_return_1d",
    "median_return_1d",
    "btc_return_1d",
    "btc_return_7d",
    "btc_return_30d",
    "eth_return_1d",
    "eth_return_7d",
    "eth_return_30d",
    "btc_relative_strength_7d",
    "eth_relative_strength_7d",
    "rs_vs_btc_1d",
    "rs_vs_btc_7d",
    "rs_vs_btc_30d",
    "rs_vs_eth_1d",
    "rs_vs_eth_7d",
    "rs_vs_eth_30d",
    "relative_strength_1d",
    "relative_strength_7d",
    "relative_strength_30d",
    "price_change_percentage_24h",
    "price_change_percentage_7d_in_currency",
    "price_change_percentage_30d_in_currency",
}
RATIO_PERCENT_COLUMNS = {
    "breadth_24h",
    "breadth_7d",
    "breadth_30d",
    "breadth_1d",
    "positive_breadth_pct",
    "positive_24h_share",
    "top_token_market_cap_share",
    "top_1_market_cap_share",
    "top_3_market_cap_share",
    "top_1_volume_share",
    "top_3_volume_share",
    "volume_share_within_narrative",
    "market_cap_share_within_narrative",
    "market_cap_share_pct",
    "volume_to_market_cap",
    "avg_volume_to_market_cap",
    "volume_share_pct",
}
MONEY_COLUMNS = {
    "market_cap",
    "total_market_cap",
    "total_market_cap_usd",
    "total_volume",
    "total_volume_usd",
    "top_token_market_cap",
    "top_token_market_cap_usd",
    "top_1_market_cap",
    "top_3_market_cap",
}
COMPONENT_SCORE_COLUMNS = [
    "price_momentum_score",
    "relative_strength_score",
    "volume_confirmation_score",
    "breadth_score",
]
SCORE_WEIGHT_ROWS = [
    {
        "component": "Price momentum",
        "weight": "40%",
        "description": "24h, 7D, and 30D median return context.",
    },
    {
        "component": "Relative strength",
        "weight": "25%",
        "description": "7D median return compared with BTC and ETH.",
    },
    {
        "component": "Volume confirmation",
        "weight": "20%",
        "description": "Volume-to-market-cap activity context.",
    },
    {
        "component": "Breadth of participation",
        "weight": "15%",
        "description": "Share of tokens participating across return windows.",
    },
]
RETURN_SKEW_REVIEW_THRESHOLD_PP = 3.0
RETURN_DISPERSION_IQR_MULTIPLE = 2.0
RETURN_SKEW_RETURN_COLUMN = "price_change_percentage_7d_in_currency"
RETURN_SKEW_OUTPUT_COLUMNS = [
    "primary_narrative",
    "token_count",
    "avg_return_7d",
    "median_return_7d",
    "mean_median_gap_pp",
    "return_iqr_7d",
    "median_return_iqr_7d_across_narratives",
    "top_return_symbol",
    "top_return_7d",
    "bottom_return_symbol",
    "bottom_return_7d",
    "top_return_token",
    "bottom_return_token",
    "skew_trigger",
    "dispersion_trigger",
    "skew_review_flag",
    "diagnostic_note",
]

COLUMN_LABELS = {
    "rank": "Rank",
    "primary_narrative": "Narrative",
    "token_count": "Token Count",
    "narrative_momentum_score": "Narrative Momentum Score",
    "momentum_score": "Narrative Momentum Score",
    "price_momentum_score": "Price Momentum Score",
    "relative_strength_score": "Relative Strength Score",
    "volume_confirmation_score": "Volume Confirmation Score",
    "breadth_score": "Breadth Score",
    "scoring_note": "Scoring Note",
    "avg_return_7d": "Mean 7D Return",
    "avg_return_30d": "Mean 30D Return",
    "median_return_7d": "Median 7D Return",
    "median_return_30d": "Median 30D Return",
    "total_market_cap": "Total Market Cap",
    "total_market_cap_usd": "Total Market Cap",
    "total_volume": "Total Volume",
    "total_volume_usd": "Total Volume",
    "breadth_7d": "7D Breadth",
    "positive_breadth_pct": "Positive Breadth",
    "rs_vs_btc_7d": "RS vs BTC 7D",
    "rs_vs_eth_7d": "RS vs ETH 7D",
    "rs_vs_btc_30d": "RS vs BTC 30D",
    "rs_vs_eth_30d": "RS vs ETH 30D",
    "relative_strength_7d": "Avg RS vs BTC/ETH 7D",
    "relative_strength_30d": "Relative Strength 30D",
    "concentration_flag": "Concentration",
    "current_price": "Price",
    "symbol": "Symbol",
    "name": "Name",
    "market_cap": "Market Cap",
    "price_change_percentage_24h": "24H Return",
    "price_change_percentage_7d_in_currency": "7D Return",
    "price_change_percentage_30d_in_currency": "30D Return",
    "volume_share_within_narrative": "Volume Share",
    "market_cap_share_within_narrative": "Market Cap Share",
    "top_1_market_cap_share": "Top 1 Market Cap Share",
    "top_3_market_cap_share": "Top 3 Market Cap Share",
    "concentration_comment": "Concentration Comment",
    "volume_share_pct": "Volume Share",
    "mean_median_gap_pp": "Mean-Median Gap",
    "return_iqr_7d": "7D Return IQR",
    "median_return_iqr_7d_across_narratives": "Snapshot Median 7D Return IQR",
    "top_return_symbol": "Top 7D Token",
    "top_return_7d": "Top 7D Return",
    "bottom_return_symbol": "Bottom 7D Token",
    "bottom_return_7d": "Bottom 7D Return",
    "top_return_token": "Top 7D Token",
    "bottom_return_token": "Bottom 7D Token",
    "skew_review_flag": "Review Flag",
    "diagnostic_note": "Diagnostic Note",
}
PERCENTAGE_POINT_GAP_COLUMNS = {
    "mean_median_gap_pp",
    "return_iqr_7d",
}


def find_latest_processed_date(processed_root: Path = PROCESSED_DATA_DIR) -> str:
    """Return the latest date-like processed folder."""
    if not processed_root.exists():
        raise FileNotFoundError(f"Processed data folder not found: {processed_root}")
    date_dirs = [
        path.name
        for path in processed_root.iterdir()
        if path.is_dir() and DATE_PATTERN.match(path.name)
    ]
    if not date_dirs:
        raise FileNotFoundError(f"No date-like processed folders found in {processed_root}")
    return sorted(date_dirs)[-1]


def get_snapshot_paths(snapshot_date: str, processed_root: Path = PROCESSED_DATA_DIR) -> dict[str, Path]:
    """Return expected input paths for a processed snapshot date."""
    processed_dir = processed_root / snapshot_date
    return {
        "processed_dir": processed_dir,
        "narrative_ranking": processed_dir / "narrative_ranking.csv",
        "narrative_metrics": processed_dir / "narrative_metrics.csv",
        "token_snapshot": processed_dir / TOKEN_SNAPSHOT_TEMPLATE.format(snapshot_date=snapshot_date),
        "sql_top_token_contributors": processed_dir / "sql_top_token_contributors.csv",
        "sql_concentration_review": processed_dir / "sql_concentration_review.csv",
        "sql_narrative_summary": processed_dir / "sql_narrative_summary.csv",
        "historical_narrative": processed_root / "historical" / "narrative_market_history_90d.csv",
    }


def load_required_csv(path: Path) -> pd.DataFrame:
    """Load a required CSV file or raise a clear error."""
    if not path.exists():
        raise FileNotFoundError(f"Required report input missing: {path}")
    return pd.read_csv(path)


def load_optional_csv(path: Path) -> pd.DataFrame | None:
    """Load an optional CSV file, returning None when unavailable."""
    if not path.exists():
        return None
    return pd.read_csv(path)


def detect_score_column(df: pd.DataFrame) -> str:
    """Return the available narrative momentum score column."""
    for column in ("momentum_score", "narrative_momentum_score"):
        if column in df.columns:
            return column
    raise ValueError(
        "Narrative ranking missing score column: expected momentum_score or "
        "narrative_momentum_score."
    )


def _is_blank(series: pd.Series) -> pd.Series:
    return series.isna() | (series.astype(str).str.strip() == "")


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(df[column], errors="coerce")


def _unparseable_count(df: pd.DataFrame, column: str, numeric: pd.Series) -> int:
    raw = df[column]
    non_blank = ~_is_blank(raw)
    return int((non_blank & numeric.isna()).sum())


def _sample_values(series: pd.Series, limit: int = 5) -> str:
    values = series.dropna().astype(str).drop_duplicates().head(limit).tolist()
    return ", ".join(values)


def _append_unique(warnings: list[str], warning: str) -> None:
    if warning not in warnings:
        warnings.append(warning)


def _warn_missing_or_nonpositive_numeric(
    warnings: list[str],
    df: pd.DataFrame,
    dataset_label: str,
    column: str,
    display_label: str,
    warn_nonpositive: bool = True,
) -> None:
    if column not in df.columns:
        _append_unique(
            warnings,
            f"{dataset_label} is missing {column}; {display_label} QA could not be completed.",
        )
        return

    numeric = _numeric_series(df, column)
    unparseable_count = _unparseable_count(df, column, numeric)
    missing_count = int(numeric.isna().sum())
    if missing_count:
        _append_unique(
            warnings,
            f"{dataset_label} has {missing_count} missing or unparseable {display_label} value(s).",
        )

    if warn_nonpositive:
        nonpositive_count = int((numeric <= 0).sum())
        if nonpositive_count:
            _append_unique(
                warnings,
                f"{dataset_label} has {nonpositive_count} nonpositive {display_label} value(s).",
            )


def _warn_extreme_percent_point_columns(
    warnings: list[str],
    df: pd.DataFrame,
    dataset_label: str,
    columns: tuple[str, ...],
    threshold: float = 100.0,
) -> None:
    for column in columns:
        if column not in df.columns:
            continue
        numeric = _numeric_series(df, column)
        unparseable_count = _unparseable_count(df, column, numeric)
        if unparseable_count:
            _append_unique(
                warnings,
                f"{dataset_label} has {unparseable_count} unparseable {COLUMN_LABELS.get(column, column)} value(s).",
            )
        extreme = numeric.abs() > threshold
        if bool(extreme.any()):
            max_abs = numeric.loc[extreme].abs().max()
            _append_unique(
                warnings,
                f"{dataset_label} has {int(extreme.sum())} {COLUMN_LABELS.get(column, column)} value(s) above {threshold:.0f}% absolute; max absolute value is {max_abs:,.1f}%. Review for data sanity.",
            )


def _warn_missing_values(
    warnings: list[str],
    df: pd.DataFrame,
    dataset_label: str,
    columns: list[str],
) -> None:
    for column in columns:
        if column not in df.columns:
            continue
        missing_count = int(_is_blank(df[column]).sum())
        if missing_count:
            _append_unique(
                warnings,
                f"{dataset_label} has {missing_count} missing {COLUMN_LABELS.get(column, column)} value(s).",
            )


def _validate_required_ranking_structure(ranking_df: pd.DataFrame) -> None:
    if ranking_df.empty:
        raise ValueError("Narrative ranking is empty.")
    if "primary_narrative" not in ranking_df.columns:
        raise ValueError("Narrative ranking missing required column: primary_narrative.")
    detect_score_column(ranking_df)


def _qa_token_snapshot(
    token_snapshot_df: pd.DataFrame | None,
    generated_at: datetime,
) -> list[str]:
    warnings: list[str] = []
    if token_snapshot_df is None:
        return warnings
    if token_snapshot_df.empty:
        return ["Token snapshot is empty; token-level QA could not be completed."]

    dataset_label = "Token snapshot"
    if "coingecko_id" in token_snapshot_df.columns:
        ids = token_snapshot_df["coingecko_id"].dropna().astype(str).str.strip().str.lower()
        duplicated_ids = ids[ids.duplicated(keep=False)]
        if not duplicated_ids.empty:
            _append_unique(
                warnings,
                f"{dataset_label} has {duplicated_ids.nunique()} duplicate CoinGecko ID(s): {_sample_values(duplicated_ids)}.",
            )
    else:
        _append_unique(warnings, f"{dataset_label} is missing coingecko_id; duplicate-token QA could not be completed.")

    if "symbol" in token_snapshot_df.columns:
        blank_symbol_count = int(_is_blank(token_snapshot_df["symbol"]).sum())
        if blank_symbol_count:
            _append_unique(
                warnings,
                f"{dataset_label} has {blank_symbol_count} missing or blank symbol value(s).",
            )
    else:
        _append_unique(warnings, f"{dataset_label} is missing symbol.")

    _warn_missing_or_nonpositive_numeric(
        warnings,
        token_snapshot_df,
        dataset_label,
        "current_price",
        "price",
    )
    _warn_missing_or_nonpositive_numeric(
        warnings,
        token_snapshot_df,
        dataset_label,
        "market_cap",
        "market cap",
    )
    _warn_missing_or_nonpositive_numeric(
        warnings,
        token_snapshot_df,
        dataset_label,
        "total_volume",
        "total volume",
        warn_nonpositive=False,
    )

    if "last_updated" in token_snapshot_df.columns:
        parsed_dates = pd.to_datetime(
            token_snapshot_df["last_updated"],
            errors="coerce",
            utc=True,
        )
        invalid_count = int(parsed_dates.isna().sum())
        if invalid_count:
            _append_unique(
                warnings,
                f"{dataset_label} has {invalid_count} missing or invalid last_updated value(s).",
            )
        valid_dates = parsed_dates.dropna()
        if not valid_dates.empty:
            latest_updated = valid_dates.max().to_pydatetime()
            report_time = generated_at if generated_at.tzinfo else generated_at.replace(tzinfo=timezone.utc)
            age = report_time - latest_updated
            if age > timedelta(days=STALE_MARKET_DATA_DAYS):
                _append_unique(
                    warnings,
                    f"{dataset_label} last_updated appears stale: latest market row updated {latest_updated.date().isoformat()}, {age.days} day(s) before report generation.",
                )

    _warn_extreme_percent_point_columns(
        warnings,
        token_snapshot_df,
        dataset_label,
        CURRENT_RETURN_COLUMNS,
    )
    return warnings


def _qa_narrative_outputs(
    ranking_df: pd.DataFrame,
    narrative_metrics_df: pd.DataFrame | None,
    concentration_df: pd.DataFrame | None,
) -> list[str]:
    warnings: list[str] = []
    _validate_required_ranking_structure(ranking_df)

    for dataset_label, df in [
        ("Narrative ranking", ranking_df),
        ("Narrative metrics", narrative_metrics_df),
    ]:
        if df is None:
            continue
        if "primary_narrative" in df.columns:
            blank_narratives = int(_is_blank(df["primary_narrative"]).sum())
            if blank_narratives:
                _append_unique(
                    warnings,
                    f"{dataset_label} has {blank_narratives} missing narrative value(s).",
                )
        else:
            _append_unique(warnings, f"{dataset_label} is missing primary_narrative.")

        _warn_extreme_percent_point_columns(
            warnings,
            df,
            dataset_label,
            CURRENT_NARRATIVE_RETURN_COLUMNS,
        )

        breadth_columns = [
            column for column in ["breadth_7d", "positive_breadth_pct"] if column in df.columns
        ]
        if not breadth_columns:
            _append_unique(
                warnings,
                f"{dataset_label} is missing breadth fields used for participation review.",
            )
        else:
            _warn_missing_values(warnings, df, dataset_label, breadth_columns)

    if concentration_df is not None:
        required_concentration_columns = [
            "primary_narrative",
            "top_1_market_cap_share",
            "top_3_market_cap_share",
            "concentration_comment",
        ]
        missing_columns = [
            column for column in required_concentration_columns if column not in concentration_df.columns
        ]
        if missing_columns:
            _append_unique(
                warnings,
                "Concentration review is missing expected column(s): "
                + ", ".join(missing_columns)
                + ".",
            )
        else:
            _warn_missing_values(
                warnings,
                concentration_df,
                "Concentration review",
                required_concentration_columns,
            )
    elif "concentration_flag" not in ranking_df.columns:
        _append_unique(
            warnings,
            "Concentration values are not available in ranking or concentration review outputs.",
        )

    return warnings


def _qa_historical_narrative(
    historical_df: pd.DataFrame | None,
    expected_narratives: set[str],
) -> list[str]:
    warnings: list[str] = []
    if historical_df is None:
        return warnings
    if historical_df.empty:
        return ["Historical narrative data is empty; 90-day context QA could not be completed."]

    dataset_label = "Historical narrative data"
    if "date" not in historical_df.columns:
        _append_unique(warnings, f"{dataset_label} is missing date.")
        return warnings
    if "primary_narrative" not in historical_df.columns:
        _append_unique(warnings, f"{dataset_label} is missing primary_narrative.")
        return warnings

    parsed_dates = pd.to_datetime(historical_df["date"], errors="coerce")
    invalid_date_count = int(parsed_dates.isna().sum())
    if invalid_date_count:
        _append_unique(
            warnings,
            f"{dataset_label} has {invalid_date_count} missing or invalid date value(s).",
        )
    blank_narrative_count = int(_is_blank(historical_df["primary_narrative"]).sum())
    if blank_narrative_count:
        _append_unique(
            warnings,
            f"{dataset_label} has {blank_narrative_count} missing narrative value(s).",
        )

    working = historical_df.copy()
    working["_parsed_date"] = parsed_dates
    working = working.dropna(subset=["_parsed_date"])
    if working.empty:
        _append_unique(
            warnings,
            f"{dataset_label} has no valid dated rows for coverage checks.",
        )
    else:
        latest_date = working["_parsed_date"].max()
        latest_rows = working.loc[working["_parsed_date"] == latest_date]
        latest_narratives = set(
            latest_rows["primary_narrative"].dropna().astype(str).str.strip()
        )
        missing_narratives = sorted(expected_narratives - latest_narratives)
        if missing_narratives:
            _append_unique(
                warnings,
                f"{dataset_label} latest date is missing expected narrative(s): {', '.join(missing_narratives)}.",
            )

    for column in HISTORICAL_RATIO_PERCENT_COLUMNS:
        if column not in historical_df.columns:
            continue
        numeric = _numeric_series(historical_df, column)
        unparseable_count = _unparseable_count(historical_df, column, numeric)
        if unparseable_count:
            _append_unique(
                warnings,
                f"{dataset_label} has {unparseable_count} unparseable {COLUMN_LABELS.get(column, column)} value(s).",
            )
        valid_numeric = numeric.dropna()
        if valid_numeric.empty:
            continue
        if column.startswith("breadth"):
            outside_ratio = (valid_numeric < 0) | (valid_numeric > 1)
            if bool(outside_ratio.any()):
                _append_unique(
                    warnings,
                    f"{dataset_label} has {int(outside_ratio.sum())} {COLUMN_LABELS.get(column, column)} value(s) outside the expected 0 to 1 ratio range.",
                )
        else:
            percent_scaled = valid_numeric.abs() > 1
            if bool(percent_scaled.any()):
                _append_unique(
                    warnings,
                    f"{dataset_label} has {int(percent_scaled.sum())} {COLUMN_LABELS.get(column, column)} value(s) above 100% on a decimal-ratio scale; confirm historical fields were not percent-point scaled.",
                )

    return warnings


def collect_report_qa_warnings(
    snapshot_date: str,
    ranking_df: pd.DataFrame,
    narrative_metrics_df: pd.DataFrame | None = None,
    token_snapshot_df: pd.DataFrame | None = None,
    concentration_df: pd.DataFrame | None = None,
    historical_df: pd.DataFrame | None = None,
    generated_at: datetime | None = None,
) -> list[str]:
    """Collect data sanity warnings for CSV inputs used by the HTML report."""
    report_time = generated_at or datetime.now(timezone.utc)
    _validate_required_ranking_structure(ranking_df)
    expected_narratives = set(
        ranking_df["primary_narrative"].dropna().astype(str).str.strip()
    )
    warnings: list[str] = []
    warnings.extend(_qa_token_snapshot(token_snapshot_df, report_time))
    warnings.extend(
        _qa_narrative_outputs(ranking_df, narrative_metrics_df, concentration_df)
    )
    warnings.extend(_qa_historical_narrative(historical_df, expected_narratives))
    if snapshot_date and not DATE_PATTERN.match(str(snapshot_date)):
        _append_unique(
            warnings,
            f"Snapshot date {snapshot_date} is not in YYYY-MM-DD format.",
        )
    return warnings


def _is_stale_market_data_warning(warning: str) -> bool:
    return "last_updated appears stale" in warning


def _sample_report_qa_warnings(warnings: list[str]) -> list[str]:
    return [
        warning
        for warning in warnings
        if not _is_stale_market_data_warning(warning)
    ]


def _row_for_extreme(df: pd.DataFrame, column: str, ascending: bool) -> dict[str, Any] | None:
    if column not in df.columns or "primary_narrative" not in df.columns:
        return None
    working = df.copy()
    working[column] = pd.to_numeric(working[column], errors="coerce")
    working = working.dropna(subset=[column])
    if working.empty:
        return None
    row = working.sort_values(column, ascending=ascending).iloc[0]
    return row.to_dict()


def _metric_label(column: str) -> str:
    labels = {
        "narrative_momentum_score": "Narrative Momentum Score",
        "momentum_score": "Narrative Momentum Score",
        "avg_return_7d": "Mean 7D Return",
        "avg_return_30d": "Mean 30D Return",
        "positive_breadth_pct": "Positive Breadth",
        "breadth_7d": "7D Breadth",
        "top_3_market_cap_share": "Top 3 Market Cap Share",
    }
    return labels.get(column, column.replace("_", " ").title())


def _card(title: str, row: dict[str, Any] | None, column: str, note: str) -> dict[str, str]:
    if not row:
        return {"title": title, "narrative": "Not available", "value": "n/a", "note": note}
    return {
        "title": title,
        "narrative": str(row.get("primary_narrative", "Not available")),
        "value": format_value(row.get(column), column),
        "note": note,
    }


def _format_signed_percent_point(value: Any) -> str:
    numeric = _numeric_value(value)
    if numeric is None:
        return "N/A"
    return f"{numeric:+,.1f}%"


def _row_for_narrative(
    df: pd.DataFrame | None,
    narrative: str,
) -> dict[str, Any] | None:
    if df is None or df.empty or "primary_narrative" not in df.columns:
        return None
    matches = df[
        df["primary_narrative"].astype("string").str.strip() == str(narrative).strip()
    ]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()


def _return_leadership_bullet(
    strongest_7d: dict[str, Any] | None,
    return_skew_df: pd.DataFrame | None = None,
) -> str | None:
    if not strongest_7d:
        return None
    narrative = str(strongest_7d["primary_narrative"])
    skew_row = _row_for_narrative(return_skew_df, narrative)
    mean_return = (
        skew_row.get("avg_return_7d")
        if skew_row is not None
        else strongest_7d.get("avg_return_7d")
    )
    median_return = (
        skew_row.get("median_return_7d")
        if skew_row is not None
        else strongest_7d.get("median_return_7d")
    )
    review_flag = str(skew_row.get("skew_review_flag", "No Review")) if skew_row else "No Review"

    if skew_row is not None and review_flag != "No Review":
        top_symbol = _clean_text_value(skew_row.get("top_return_symbol"))
        top_return = skew_row.get("top_return_7d")
        descriptor = (
            "least-negative 7D return context by mean"
            if (_numeric_value(mean_return) or 0) < 0
            else "strongest mean 7D return context"
        )
        flag_text = "skew-flagged" if "Skew" in review_flag else "review-flagged"
        return (
            f"{narrative} had the {descriptor}, but this was {flag_text}: "
            f"mean 7D return was {_format_signed_percent_point(mean_return)} "
            f"while median 7D return was {_format_signed_percent_point(median_return)}, "
            f"with {top_symbol} as the strongest 7D token at "
            f"{_format_signed_percent_point(top_return)}."
        )

    return (
        f"{narrative} showed the strongest mean 7D return context at "
        f"{_format_signed_percent_point(mean_return)}, with median 7D return at "
        f"{_format_signed_percent_point(median_return)}."
    )


def prepare_executive_summary(
    ranking_df: pd.DataFrame,
    concentration_df: pd.DataFrame | None = None,
    return_skew_df: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Prepare top-level descriptive insights for the research report."""
    score_column = detect_score_column(ranking_df)
    top_score = _row_for_extreme(ranking_df, score_column, ascending=False)
    weakest_score = _row_for_extreme(ranking_df, score_column, ascending=True)
    strongest_7d = _row_for_extreme(ranking_df, "avg_return_7d", ascending=False)
    strongest_30d = _row_for_extreme(ranking_df, "avg_return_30d", ascending=False)
    breadth_column = "positive_breadth_pct" if "positive_breadth_pct" in ranking_df.columns else "breadth_7d"
    broadest = _row_for_extreme(ranking_df, breadth_column, ascending=False)
    highest_concentration = (
        _row_for_extreme(concentration_df, "top_3_market_cap_share", ascending=False)
        if concentration_df is not None
        else None
    )
    cards = [
        _card(
            "Top Narrative by Momentum",
            top_score,
            score_column,
            "Current narrative leadership based on the research ranking.",
        ),
        _card(
            "Strongest 7D Narrative",
            strongest_7d,
            "avg_return_7d",
            "Recent return context, not a trading recommendation.",
        ),
        _card(
            "Strongest 30D Narrative",
            strongest_30d,
            "avg_return_30d",
            "Medium-window return context for narrative-level analysis.",
        ),
        _card(
            "Broadest Participation",
            broadest,
            breadth_column,
            "Breadth helps show whether participation is broad across a narrative.",
        ),
        _card(
            "Weakest Relative Momentum",
            weakest_score,
            score_column,
            "Lagging narrative momentum in the current snapshot.",
        ),
        _card(
            "Highest Concentration",
            highest_concentration,
            "top_3_market_cap_share",
            "Concentration context shows whether activity is driven by a few large tokens.",
        ),
    ]
    bullets = []
    if top_score:
        bullets.append(
            f"{top_score['primary_narrative']} leads the current Narrative Momentum Score at "
            f"{format_value(top_score.get(score_column), score_column)}."
        )
    return_bullet = _return_leadership_bullet(strongest_7d, return_skew_df)
    if return_bullet:
        bullets.append(return_bullet)
    if strongest_30d:
        bullets.append(
            f"{strongest_30d['primary_narrative']} shows the strongest 30D return context at "
            f"{format_value(strongest_30d.get('avg_return_30d'), 'avg_return_30d')}."
        )
    if broadest:
        bullets.append(
            f"{broadest['primary_narrative']} has the broadest participation using "
            f"{_metric_label(breadth_column)} at {format_value(broadest.get(breadth_column), breadth_column)}."
        )
    if weakest_score:
        bullets.append(
            f"{weakest_score['primary_narrative']} has softer relative momentum in this snapshot."
        )
    if highest_concentration:
        bullets.append(
            f"{highest_concentration['primary_narrative']} has the highest top-three market cap concentration at "
            f"{format_value(highest_concentration.get('top_3_market_cap_share'), 'top_3_market_cap_share')}."
        )
    return {
        "score_column": score_column,
        "cards": cards,
        "bullets": bullets,
        "top_score": top_score,
        "weakest_score": weakest_score,
    }


def _select_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    available = [column for column in columns if column in df.columns]
    return df[available].copy() if available else pd.DataFrame()


def _records(
    df: pd.DataFrame,
    max_rows: int | None = None,
    column_formats: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    if df.empty:
        return None
    if max_rows is not None:
        df = df.head(max_rows)
    columns = list(df.columns)
    return {
        "columns": columns,
        "labels": {column: COLUMN_LABELS.get(column, column.replace("_", " ").title()) for column in columns},
        "formats": column_formats or {},
        "rows": df.to_dict(orient="records"),
    }


def _table_from_df(
    df: pd.DataFrame,
    columns: list[str],
    max_rows: int | None = None,
    column_formats: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    selected = _select_columns(df, columns)
    return _records(selected, max_rows=max_rows, column_formats=column_formats)


def _component_breakdown_table(
    ranking_df: pd.DataFrame,
    score_column: str,
) -> dict[str, Any] | None:
    if not all(column in ranking_df.columns for column in COMPONENT_SCORE_COLUMNS):
        return None
    columns = [
        "rank",
        "primary_narrative",
        score_column,
        *COMPONENT_SCORE_COLUMNS,
        "scoring_note",
    ]
    return _table_from_df(ranking_df, columns)


def _sanitize_concentration_review(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None or df.empty or "concentration_comment" not in df.columns:
        return df
    working = df.copy()
    working["concentration_comment"] = (
        working["concentration_comment"]
        .astype("string")
        .str.replace(
            "Broad participation:",
            "Lower concentration:",
            regex=False,
        )
    )
    return working


def _clean_text_value(value: Any, fallback: str = "N/A") -> str:
    if value is None or pd.isna(value):
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _token_count(group: pd.DataFrame) -> int:
    if "coingecko_id" not in group.columns:
        return int(len(group))
    ids = group["coingecko_id"].dropna().astype(str).str.strip()
    ids = ids[ids != ""]
    if ids.empty:
        return int(len(group))
    return int(ids.nunique())


def _token_return_label(symbol: str, return_value: Any) -> str:
    if symbol == "N/A" or _numeric_value(return_value) is None:
        return "N/A"
    return f"{symbol} ({format_percent_point(return_value)})"


def _return_extremes_sentence(
    top_symbol: str,
    top_return: float | None,
    bottom_symbol: str,
    bottom_return: float | None,
) -> str:
    return (
        f"Top 7D token was {top_symbol} at {format_percent_point(top_return)}; "
        f"bottom 7D token was {bottom_symbol} at {format_percent_point(bottom_return)}."
    )


def _review_flag(skew_trigger: bool, dispersion_trigger: bool) -> str:
    if skew_trigger and dispersion_trigger:
        return "Skew + Dispersion Review"
    if skew_trigger:
        return "Skew Review"
    if dispersion_trigger:
        return "Dispersion Review"
    return "No Review"


def _diagnostic_note(
    gap: float | None,
    return_iqr: float | None,
    median_return_iqr: float | None,
    top_symbol: str,
    top_return: float | None,
    bottom_symbol: str,
    bottom_return: float | None,
    skew_trigger: bool,
    dispersion_trigger: bool,
) -> str:
    if gap is None or return_iqr is None:
        return "7D return data was not available for this narrative."
    extremes = _return_extremes_sentence(
        top_symbol,
        top_return,
        bottom_symbol,
        bottom_return,
    )
    gap_text = format_percentage_point_gap(gap)
    iqr_text = format_percentage_point_gap(return_iqr)
    median_iqr_text = format_percentage_point_gap(median_return_iqr)
    if skew_trigger and dispersion_trigger:
        return (
            f"Mean-median gap was {gap_text} and 7D return IQR was {iqr_text} "
            f"versus snapshot median IQR of {median_iqr_text}. {extremes}"
        )
    if skew_trigger:
        return f"Mean-median gap was {gap_text}. {extremes}"
    if dispersion_trigger:
        return (
            f"7D return IQR was {iqr_text} versus snapshot median IQR of "
            f"{median_iqr_text}. {extremes}"
        )
    return (
        f"Mean-median gap was {gap_text} and 7D return IQR was {iqr_text}; "
        "neither exceeded V1 review thresholds."
    )


def calculate_return_skew_diagnostics(
    token_snapshot_df: pd.DataFrame | None,
) -> pd.DataFrame:
    """Calculate descriptive 7D return skew diagnostics by primary narrative."""
    required_columns = {"primary_narrative", RETURN_SKEW_RETURN_COLUMN}
    if (
        token_snapshot_df is None
        or token_snapshot_df.empty
        or not required_columns.issubset(token_snapshot_df.columns)
    ):
        return pd.DataFrame(columns=RETURN_SKEW_OUTPUT_COLUMNS)

    working = token_snapshot_df.copy()
    if "symbol" not in working.columns:
        working["symbol"] = pd.NA
    working["primary_narrative"] = (
        working["primary_narrative"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
        .fillna("Unknown")
    )
    working[RETURN_SKEW_RETURN_COLUMN] = pd.to_numeric(
        working[RETURN_SKEW_RETURN_COLUMN],
        errors="coerce",
    )

    records: list[dict[str, Any]] = []
    grouped = working.groupby("primary_narrative", dropna=False, sort=True)
    for narrative, group in grouped:
        valid_returns = group[RETURN_SKEW_RETURN_COLUMN].dropna()
        record: dict[str, Any] = {
            "primary_narrative": str(narrative),
            "token_count": _token_count(group),
            "avg_return_7d": pd.NA,
            "median_return_7d": pd.NA,
            "mean_median_gap_pp": pd.NA,
            "return_iqr_7d": pd.NA,
            "median_return_iqr_7d_across_narratives": pd.NA,
            "top_return_symbol": "N/A",
            "top_return_7d": pd.NA,
            "bottom_return_symbol": "N/A",
            "bottom_return_7d": pd.NA,
            "top_return_token": "N/A",
            "bottom_return_token": "N/A",
            "skew_trigger": False,
            "dispersion_trigger": False,
            "skew_review_flag": "No Review",
            "diagnostic_note": "7D return data was not available for this narrative.",
        }
        if valid_returns.empty:
            records.append(record)
            continue

        valid_rows = group.dropna(subset=[RETURN_SKEW_RETURN_COLUMN]).copy()
        valid_rows["_symbol_sort"] = valid_rows["symbol"].astype("string").fillna("")
        top_row = valid_rows.sort_values(
            [RETURN_SKEW_RETURN_COLUMN, "_symbol_sort"],
            ascending=[False, True],
        ).iloc[0]
        bottom_row = valid_rows.sort_values(
            [RETURN_SKEW_RETURN_COLUMN, "_symbol_sort"],
            ascending=[True, True],
        ).iloc[0]
        avg_return_7d = float(valid_returns.mean())
        median_return_7d = float(valid_returns.median())
        mean_median_gap_pp = avg_return_7d - median_return_7d
        return_iqr_7d = float(valid_returns.quantile(0.75) - valid_returns.quantile(0.25))
        top_symbol = _clean_text_value(top_row.get("symbol"))
        bottom_symbol = _clean_text_value(bottom_row.get("symbol"))
        top_return_7d = float(top_row[RETURN_SKEW_RETURN_COLUMN])
        bottom_return_7d = float(bottom_row[RETURN_SKEW_RETURN_COLUMN])

        record.update(
            {
                "avg_return_7d": avg_return_7d,
                "median_return_7d": median_return_7d,
                "mean_median_gap_pp": mean_median_gap_pp,
                "return_iqr_7d": return_iqr_7d,
                "top_return_symbol": top_symbol,
                "top_return_7d": top_return_7d,
                "bottom_return_symbol": bottom_symbol,
                "bottom_return_7d": bottom_return_7d,
                "top_return_token": _token_return_label(top_symbol, top_return_7d),
                "bottom_return_token": _token_return_label(
                    bottom_symbol,
                    bottom_return_7d,
                ),
            }
        )
        records.append(record)

    median_return_iqr = _numeric_value(
        pd.Series(
            [record["return_iqr_7d"] for record in records],
            dtype="Float64",
        ).median()
    )
    dispersion_threshold = (
        RETURN_DISPERSION_IQR_MULTIPLE * median_return_iqr
        if median_return_iqr is not None
        else None
    )
    for record in records:
        gap = _numeric_value(record["mean_median_gap_pp"])
        return_iqr = _numeric_value(record["return_iqr_7d"])
        skew_trigger = (
            abs(gap) >= RETURN_SKEW_REVIEW_THRESHOLD_PP
            if gap is not None
            else False
        )
        dispersion_trigger = (
            return_iqr is not None
            and median_return_iqr is not None
            and dispersion_threshold is not None
            and return_iqr >= dispersion_threshold
            and (median_return_iqr > 0 or return_iqr > 0)
        )
        record["median_return_iqr_7d_across_narratives"] = (
            median_return_iqr if median_return_iqr is not None else pd.NA
        )
        record["skew_trigger"] = bool(skew_trigger)
        record["dispersion_trigger"] = bool(dispersion_trigger)
        record["skew_review_flag"] = _review_flag(
            bool(skew_trigger),
            bool(dispersion_trigger),
        )
        record["diagnostic_note"] = _diagnostic_note(
            gap,
            return_iqr,
            median_return_iqr,
            record["top_return_symbol"],
            _numeric_value(record["top_return_7d"]),
            record["bottom_return_symbol"],
            _numeric_value(record["bottom_return_7d"]),
            bool(skew_trigger),
            bool(dispersion_trigger),
        )

    return pd.DataFrame(records, columns=RETURN_SKEW_OUTPUT_COLUMNS)


def _methodology_context() -> dict[str, Any]:
    return {
        "score_weights": SCORE_WEIGHT_ROWS,
        "score_note": (
            "Narrative Momentum Score is a relative research ranking score, "
            "not statistical confidence."
        ),
        "normalization_note": (
            "Component scores are percentile-rank normalized within the current "
            "narrative universe using the existing pandas rank percentile method."
        ),
        "relative_strength_note": (
            "Relative Strength 7D averages median narrative 7D return minus BTC "
            "7D return and median narrative 7D return minus ETH 7D return."
        ),
        "concentration_note": (
            "Concentration labels and comments are judgment-based V1 heuristics, "
            "not statistically derived cutoffs."
        ),
        "token_universe_note": (
            "The token universe is 80 manually curated tokens: 10 representative "
            "tokens per narrative, not full sector coverage."
        ),
        "taxonomy_note": (
            "Taxonomy assignments involve judgment and can miss sector breadth "
            "or token overlap."
        ),
        "return_skew_note": (
            "Return skew diagnostics are descriptive only. Skew and dispersion "
            "review thresholds are judgment-based V1 review heuristics, not "
            "statistically derived cutoffs. The IQR threshold is "
            "snapshot-relative: each narrative's 7D return IQR is compared "
            "with two times the median narrative 7D return IQR in the same "
            "report snapshot, not an absolute cross-date threshold. These "
            "diagnostics do not affect the Narrative Momentum Score. The "
            "review flag does not imply an investment recommendation."
        ),
    }


def _sort_by_score(df: pd.DataFrame, score_column: str, ascending: bool) -> pd.DataFrame:
    working = df.copy()
    working[score_column] = pd.to_numeric(working[score_column], errors="coerce")
    return working.sort_values([score_column, "primary_narrative"], ascending=[ascending, True])


def _chart_pct(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def _axis_position(value: float | None, axis_min: float, axis_max: float) -> float | None:
    if value is None or axis_max == axis_min:
        return None
    return _chart_pct(((value - axis_min) / (axis_max - axis_min)) * 100)


def _review_flag_class(flag: Any) -> str:
    label = str(flag or "No Review").lower()
    css_name = re.sub(r"[^a-z0-9]+", "-", label).strip("-")
    return css_name or "no-review"


def _prepare_score_chart(ranking_df: pd.DataFrame, score_column: str) -> dict[str, Any]:
    if (
        ranking_df.empty
        or "primary_narrative" not in ranking_df.columns
        or score_column not in ranking_df.columns
    ):
        return {"available": False, "rows": []}
    working = ranking_df[["primary_narrative", score_column]].copy()
    working[score_column] = pd.to_numeric(working[score_column], errors="coerce")
    working = working.dropna(subset=[score_column])
    if working.empty:
        return {"available": False, "rows": []}
    working = working.sort_values(
        [score_column, "primary_narrative"],
        ascending=[False, True],
    )
    rows = []
    for row in working.to_dict(orient="records"):
        score = float(row[score_column])
        rows.append(
            {
                "primary_narrative": str(row["primary_narrative"]),
                "score": score,
                "score_label": format_value(score, score_column),
                "width_pct": _chart_pct(score),
            }
        )
    return {
        "available": True,
        "score_column": score_column,
        "score_label": COLUMN_LABELS.get(score_column, "Narrative Momentum Score"),
        "rows": rows,
    }


def _prepare_return_skew_chart(return_skew_df: pd.DataFrame) -> dict[str, Any]:
    required_columns = {
        "primary_narrative",
        "avg_return_7d",
        "median_return_7d",
        "mean_median_gap_pp",
        "skew_review_flag",
    }
    if return_skew_df.empty or not required_columns.issubset(return_skew_df.columns):
        return {"available": False, "rows": []}

    working = return_skew_df.copy()
    for column in [
        "avg_return_7d",
        "median_return_7d",
        "mean_median_gap_pp",
        "return_iqr_7d",
    ]:
        if column in working.columns:
            working[column] = pd.to_numeric(working[column], errors="coerce")
    working = working.dropna(subset=["avg_return_7d", "median_return_7d"], how="all")
    if working.empty:
        return {"available": False, "rows": []}

    values = pd.concat(
        [
            working["avg_return_7d"].dropna(),
            working["median_return_7d"].dropna(),
            pd.Series([0.0]),
        ],
        ignore_index=True,
    )
    axis_min = float(values.min())
    axis_max = float(values.max())
    if axis_min == axis_max:
        axis_min -= 1.0
        axis_max += 1.0
    else:
        padding = max((axis_max - axis_min) * 0.08, 1.0)
        axis_min -= padding
        axis_max += padding

    rows = []
    for row in working.sort_values("primary_narrative").to_dict(orient="records"):
        mean_return = _numeric_value(row.get("avg_return_7d"))
        median_return = _numeric_value(row.get("median_return_7d"))
        gap = _numeric_value(row.get("mean_median_gap_pp"))
        return_iqr = _numeric_value(row.get("return_iqr_7d"))
        flag = str(row.get("skew_review_flag") or "No Review")
        rows.append(
            {
                "primary_narrative": str(row["primary_narrative"]),
                "mean_label": format_percent_point(mean_return),
                "median_label": format_percent_point(median_return),
                "gap_label": format_percentage_point_gap(gap),
                "iqr_label": format_percentage_point_gap(return_iqr),
                "mean_position_pct": _axis_position(mean_return, axis_min, axis_max),
                "median_position_pct": _axis_position(
                    median_return,
                    axis_min,
                    axis_max,
                ),
                "review_flag": flag,
                "review_flag_class": _review_flag_class(flag),
            }
        )

    return {
        "available": True,
        "axis_min_label": format_percent_point(axis_min),
        "axis_max_label": format_percent_point(axis_max),
        "zero_position_pct": _axis_position(0.0, axis_min, axis_max),
        "rows": rows,
    }


def _prepare_historical_context(history_df: pd.DataFrame | None) -> dict[str, Any]:
    if history_df is None or history_df.empty or "date" not in history_df.columns:
        return {
            "available": False,
            "note": "Historical narrative data was not available for this report.",
        }
    working = history_df.copy()
    working["date"] = pd.to_datetime(working["date"], errors="coerce")
    working = working.dropna(subset=["date"])
    if working.empty:
        return {
            "available": False,
            "note": "Historical narrative data was not available for this report.",
        }
    latest_date = working["date"].max()
    latest_rows = working.loc[working["date"] == latest_date].copy()
    historical_ratio_columns = {
        column: "ratio_pct" for column in HISTORICAL_RATIO_PERCENT_COLUMNS
    }
    table = _table_from_df(
        latest_rows.sort_values("primary_narrative"),
        [
            "primary_narrative",
            "avg_return_7d",
            "median_return_7d",
            "avg_return_30d",
            "median_return_30d",
            "breadth_7d",
            "rs_vs_btc_7d",
            "rs_vs_eth_7d",
            "rs_vs_btc_30d",
            "rs_vs_eth_30d",
            "relative_strength_7d",
            "relative_strength_30d",
            "total_market_cap_usd",
            "total_volume_usd",
        ],
        column_formats=historical_ratio_columns,
    )
    return {
        "available": True,
        "start_date": working["date"].min().date().isoformat(),
        "end_date": latest_date.date().isoformat(),
        "narrative_count": int(working["primary_narrative"].nunique())
        if "primary_narrative" in working.columns
        else 0,
        "latest_table": table,
    }


def _numeric_value(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric):
        return None
    return float(numeric)


def format_percent_point(value: Any) -> str:
    """Format a percent-point value without rescaling it."""
    numeric = _numeric_value(value)
    if numeric is None:
        return "N/A"
    return f"{numeric:,.1f}%"


def format_percentage_point_gap(value: Any) -> str:
    """Format a difference between percent-point values."""
    numeric = _numeric_value(value)
    if numeric is None:
        return "N/A"
    return f"{numeric:,.1f}pp"


def format_ratio_pct(value: Any) -> str:
    """Format a ratio value as a percentage."""
    numeric = _numeric_value(value)
    if numeric is None:
        return "N/A"
    return f"{numeric * 100:,.1f}%"


def format_value(
    value: Any,
    column: str | None = None,
    scale: str | None = None,
) -> str:
    """Format report values for readable static tables."""
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, str):
        return value
    numeric = _numeric_value(value)
    if numeric is None:
        return str(value)
    if scale == "percent_point":
        return format_percent_point(numeric)
    if scale == "percentage_point_gap":
        return format_percentage_point_gap(numeric)
    if scale == "ratio_pct":
        return format_ratio_pct(numeric)
    if column in PERCENTAGE_POINT_GAP_COLUMNS:
        return format_percentage_point_gap(numeric)
    if column in PERCENT_POINT_COLUMNS:
        return format_percent_point(numeric)
    if column in RATIO_PERCENT_COLUMNS:
        return format_ratio_pct(numeric)
    if column in MONEY_COLUMNS:
        return f"${numeric:,.0f}"
    if column and "score" in column:
        return f"{numeric:,.1f}"
    if float(numeric).is_integer():
        return f"{numeric:,.0f}"
    return f"{numeric:,.2f}"


def prepare_report_context(
    snapshot_date: str | None = None,
    processed_root: Path = PROCESSED_DATA_DIR,
    reports_root: Path = REPORTS_DIR,
    templates_root: Path = TEMPLATES_DIR,
    sample_mode: bool = False,
) -> dict[str, Any]:
    """Load processed outputs and prepare template context."""
    selected_date = (
        SAMPLE_REPORT_DATE
        if sample_mode
        else snapshot_date or find_latest_processed_date(processed_root)
    )
    paths = get_snapshot_paths(selected_date, processed_root)
    ranking_df = load_required_csv(paths["narrative_ranking"])
    narrative_metrics_df = load_optional_csv(paths["narrative_metrics"])
    token_snapshot_df = load_optional_csv(paths["token_snapshot"])
    contributors_df = load_optional_csv(paths["sql_top_token_contributors"])
    concentration_df = load_optional_csv(paths["sql_concentration_review"])
    display_concentration_df = _sanitize_concentration_review(concentration_df)
    historical_df = load_optional_csv(paths["historical_narrative"])
    return_skew_df = calculate_return_skew_diagnostics(token_snapshot_df)
    generated_at = datetime.now(timezone.utc)
    qa_warnings = collect_report_qa_warnings(
        snapshot_date=selected_date,
        ranking_df=ranking_df,
        narrative_metrics_df=narrative_metrics_df,
        token_snapshot_df=token_snapshot_df,
        concentration_df=concentration_df,
        historical_df=historical_df,
        generated_at=generated_at,
    )
    if sample_mode:
        qa_warnings = _sample_report_qa_warnings(qa_warnings)

    summary = prepare_executive_summary(ranking_df, concentration_df, return_skew_df)
    score_column = summary["score_column"]
    sorted_desc = _sort_by_score(ranking_df, score_column, ascending=False)
    sorted_asc = _sort_by_score(ranking_df, score_column, ascending=True)
    ranking_columns = [
        "rank",
        "primary_narrative",
        "token_count",
        score_column,
        "avg_return_7d",
        "median_return_7d",
        "avg_return_30d",
        "total_market_cap",
        "total_volume",
        "breadth_7d",
        "positive_breadth_pct",
        "relative_strength_7d",
        "concentration_flag",
    ]
    contributor_source = contributors_df if contributors_df is not None else token_snapshot_df
    contributor_columns = [
        "primary_narrative",
        "symbol",
        "name",
        "total_volume",
        "market_cap",
        "price_change_percentage_7d_in_currency",
        "volume_share_within_narrative",
        "market_cap_share_within_narrative",
    ]
    output_filename = (
        SAMPLE_REPORT_FILENAME_TEMPLATE.format(snapshot_date=selected_date)
        if sample_mode
        else REPORT_FILENAME_TEMPLATE.format(snapshot_date=selected_date)
    )
    return {
        "snapshot_date": selected_date,
        "generated_at": generated_at.strftime("%Y-%m-%d %H:%M UTC"),
        "is_sample_report": sample_mode,
        "sample_report_note": SAMPLE_REPORT_NOTE if sample_mode else None,
        "project_root": PROJECT_ROOT,
        "reports_root": reports_root,
        "templates_root": templates_root,
        "qa_warnings": qa_warnings,
        "summary": summary,
        "methodology": _methodology_context(),
        "top_narratives": _records(_select_columns(sorted_desc.head(3), ranking_columns)),
        "weakening_narratives": _records(_select_columns(sorted_asc.head(3), ranking_columns)),
        "ranking_table": _table_from_df(sorted_desc, ranking_columns),
        "score_component_breakdown": _component_breakdown_table(sorted_desc, score_column),
        "score_chart": _prepare_score_chart(sorted_desc, score_column),
        "return_skew_chart": _prepare_return_skew_chart(return_skew_df),
        "return_skew_diagnostics": _table_from_df(
            return_skew_df,
            [
                "primary_narrative",
                "avg_return_7d",
                "median_return_7d",
                "mean_median_gap_pp",
                "return_iqr_7d",
                "top_return_token",
                "bottom_return_token",
                "skew_review_flag",
                "diagnostic_note",
            ],
            column_formats={
                "mean_median_gap_pp": "percentage_point_gap",
                "return_iqr_7d": "percentage_point_gap",
            },
        ),
        "return_skew_note": (
            "Return skew diagnostics require token-level 7D return data and were not available for this report."
            if return_skew_df.empty
            else None
        ),
        "token_contributors": _table_from_df(
            contributor_source if contributor_source is not None else pd.DataFrame(),
            contributor_columns,
            max_rows=30,
        ),
        "token_contributor_note": (
            "Token-level contributor data was not available for this report."
            if contributor_source is None
            else None
        ),
        "concentration_review": _table_from_df(
            display_concentration_df if display_concentration_df is not None else pd.DataFrame(),
            [
                "primary_narrative",
                "top_1_market_cap_share",
                "top_3_market_cap_share",
                "concentration_comment",
            ],
        ),
        "concentration_note": (
            "Concentration review output was not available for this report."
            if concentration_df is None
            else None
        ),
        "historical": _prepare_historical_context(historical_df),
        "output_dir": reports_root / "html",
        "output_path": reports_root / "html" / output_filename,
        "latest_path": reports_root / "html" / "latest.html",
        "update_latest": not sample_mode,
    }


def render_report(
    context: dict[str, Any],
    templates_root: Path = TEMPLATES_DIR,
) -> Path:
    """Render the static HTML report and optionally update latest.html."""
    output_path = Path(context["output_path"])
    latest_path = Path(context["latest_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    environment = Environment(
        loader=FileSystemLoader(templates_root),
        autoescape=select_autoescape(["html", "xml"]),
    )
    environment.filters["format_value"] = format_value
    html = environment.get_template(TEMPLATE_NAME).render(**context)
    output_path.write_text(html, encoding="utf-8")
    if context.get("update_latest", True):
        shutil.copyfile(output_path, latest_path)
    return output_path


def publish_showcase_report(
    report_path: Path,
    showcase_dir: Path = SHOWCASE_DIR,
    snapshot_date: str = SAMPLE_REPORT_DATE,
) -> Path:
    """Copy a pinned sample report into the tracked showcase folder."""
    source_path = Path(report_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Sample report not found: {source_path}")
    showcase_dir.mkdir(parents=True, exist_ok=True)
    output_path = showcase_dir / SAMPLE_REPORT_FILENAME_TEMPLATE.format(
        snapshot_date=snapshot_date
    )
    shutil.copyfile(source_path, output_path)
    return output_path


def generate_report(
    snapshot_date: str | None = None,
    processed_root: Path = PROCESSED_DATA_DIR,
    reports_root: Path = REPORTS_DIR,
    templates_root: Path = TEMPLATES_DIR,
    sample_mode: bool = False,
) -> Path:
    """Generate a static HTML market intelligence report."""
    context = prepare_report_context(
        snapshot_date=snapshot_date,
        processed_root=processed_root,
        reports_root=reports_root,
        templates_root=templates_root,
        sample_mode=sample_mode,
    )
    return render_report(context, templates_root=templates_root)
