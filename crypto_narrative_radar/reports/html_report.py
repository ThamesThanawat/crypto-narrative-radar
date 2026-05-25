"""Static HTML research report generation."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
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
TOKEN_SNAPSHOT_TEMPLATE = "token_market_snapshot_{snapshot_date}.csv"
TEMPLATE_NAME = "research_report.html.j2"
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

COLUMN_LABELS = {
    "rank": "Rank",
    "primary_narrative": "Narrative",
    "token_count": "Token Count",
    "narrative_momentum_score": "Narrative Momentum Score",
    "momentum_score": "Narrative Momentum Score",
    "avg_return_7d": "Avg 7D Return",
    "avg_return_30d": "Avg 30D Return",
    "total_market_cap": "Total Market Cap",
    "total_market_cap_usd": "Total Market Cap",
    "total_volume": "Total Volume",
    "total_volume_usd": "Total Volume",
    "breadth_7d": "7D Breadth",
    "positive_breadth_pct": "Positive Breadth",
    "relative_strength_7d": "Relative Strength 7D",
    "relative_strength_30d": "Relative Strength 30D",
    "concentration_flag": "Concentration",
    "symbol": "Symbol",
    "name": "Name",
    "market_cap": "Market Cap",
    "price_change_percentage_7d_in_currency": "7D Return",
    "volume_share_within_narrative": "Volume Share",
    "market_cap_share_within_narrative": "Market Cap Share",
    "top_1_market_cap_share": "Top 1 Market Cap Share",
    "top_3_market_cap_share": "Top 3 Market Cap Share",
    "concentration_comment": "Concentration Comment",
    "volume_share_pct": "Volume Share",
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
        "avg_return_7d": "Avg 7D Return",
        "avg_return_30d": "Avg 30D Return",
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


def prepare_executive_summary(
    ranking_df: pd.DataFrame,
    concentration_df: pd.DataFrame | None = None,
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
    if strongest_7d:
        bullets.append(
            f"{strongest_7d['primary_narrative']} shows the strongest 7D return context at "
            f"{format_value(strongest_7d.get('avg_return_7d'), 'avg_return_7d')}."
        )
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


def _sort_by_score(df: pd.DataFrame, score_column: str, ascending: bool) -> pd.DataFrame:
    working = df.copy()
    working[score_column] = pd.to_numeric(working[score_column], errors="coerce")
    return working.sort_values([score_column, "primary_narrative"], ascending=[ascending, True])


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
        "avg_return_7d": "ratio_pct",
        "avg_return_30d": "ratio_pct",
        "breadth_7d": "ratio_pct",
        "relative_strength_7d": "ratio_pct",
        "relative_strength_30d": "ratio_pct",
    }
    table = _table_from_df(
        latest_rows.sort_values("primary_narrative"),
        [
            "primary_narrative",
            "avg_return_7d",
            "avg_return_30d",
            "breadth_7d",
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
    if scale == "ratio_pct":
        return format_ratio_pct(numeric)
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
) -> dict[str, Any]:
    """Load processed outputs and prepare template context."""
    selected_date = snapshot_date or find_latest_processed_date(processed_root)
    paths = get_snapshot_paths(selected_date, processed_root)
    ranking_df = load_required_csv(paths["narrative_ranking"])
    narrative_metrics_df = load_optional_csv(paths["narrative_metrics"])
    token_snapshot_df = load_optional_csv(paths["token_snapshot"])
    contributors_df = load_optional_csv(paths["sql_top_token_contributors"])
    concentration_df = load_optional_csv(paths["sql_concentration_review"])
    narrative_summary_df = load_optional_csv(paths["sql_narrative_summary"])
    historical_df = load_optional_csv(paths["historical_narrative"])

    summary = prepare_executive_summary(ranking_df, concentration_df)
    score_column = summary["score_column"]
    sorted_desc = _sort_by_score(ranking_df, score_column, ascending=False)
    sorted_asc = _sort_by_score(ranking_df, score_column, ascending=True)
    ranking_columns = [
        "rank",
        "primary_narrative",
        "token_count",
        score_column,
        "avg_return_7d",
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
    review_source = narrative_summary_df if narrative_summary_df is not None else narrative_metrics_df
    return {
        "snapshot_date": selected_date,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "project_root": PROJECT_ROOT,
        "reports_root": reports_root,
        "templates_root": templates_root,
        "summary": summary,
        "top_narratives": _records(_select_columns(sorted_desc.head(5), ranking_columns)),
        "weakening_narratives": _records(_select_columns(sorted_asc.head(5), ranking_columns)),
        "ranking_table": _table_from_df(sorted_desc, ranking_columns),
        "review_table": _table_from_df(
            review_source if review_source is not None else ranking_df,
            [
                "primary_narrative",
                "avg_return_7d",
                "avg_return_30d",
                "total_volume",
                "volume_share_pct",
                "positive_breadth_pct",
                "breadth_7d",
                "relative_strength_7d",
            ],
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
            concentration_df if concentration_df is not None else pd.DataFrame(),
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
        "output_path": reports_root
        / "html"
        / REPORT_FILENAME_TEMPLATE.format(snapshot_date=selected_date),
        "latest_path": reports_root / "html" / "latest.html",
    }


def render_report(
    context: dict[str, Any],
    templates_root: Path = TEMPLATES_DIR,
) -> Path:
    """Render the static HTML report and update latest.html."""
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
    shutil.copyfile(output_path, latest_path)
    return output_path


def generate_report(
    snapshot_date: str | None = None,
    processed_root: Path = PROCESSED_DATA_DIR,
    reports_root: Path = REPORTS_DIR,
    templates_root: Path = TEMPLATES_DIR,
) -> Path:
    """Generate a static HTML market intelligence report."""
    context = prepare_report_context(
        snapshot_date=snapshot_date,
        processed_root=processed_root,
        reports_root=reports_root,
        templates_root=templates_root,
    )
    return render_report(context, templates_root=templates_root)
