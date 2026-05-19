"""Streamlit dashboard for Crypto Narrative Radar."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def find_processed_snapshots(base_dir: Path = PROCESSED_DATA_DIR) -> list[str]:
    """Return available processed snapshot date folders, newest first."""
    if not base_dir.exists():
        return []
    snapshots = [
        path.name for path in base_dir.iterdir() if path.is_dir() and DATE_PATTERN.match(path.name)
    ]
    return sorted(snapshots, reverse=True)


def get_latest_snapshot_date(base_dir: Path = PROCESSED_DATA_DIR) -> str | None:
    """Return the newest processed snapshot date."""
    snapshots = find_processed_snapshots(base_dir)
    return snapshots[0] if snapshots else None


def load_csv_if_exists(path: Path) -> pd.DataFrame | None:
    """Load a CSV file if it exists, otherwise return None."""
    if not path.exists():
        return None
    return pd.read_csv(path)


def load_snapshot_data(snapshot_date: str) -> dict[str, pd.DataFrame | None]:
    """Load dashboard CSV inputs for a processed snapshot date."""
    snapshot_dir = PROCESSED_DATA_DIR / snapshot_date
    return {
        "ranking": load_csv_if_exists(snapshot_dir / "narrative_ranking.csv"),
        "metrics": load_csv_if_exists(snapshot_dir / "narrative_metrics.csv"),
        "token_snapshot": load_csv_if_exists(
            snapshot_dir / f"token_market_snapshot_{snapshot_date}.csv"
        ),
        "sql_summary": load_csv_if_exists(snapshot_dir / "sql_narrative_summary.csv"),
        "contributors": load_csv_if_exists(snapshot_dir / "sql_top_token_contributors.csv"),
        "concentration": load_csv_if_exists(snapshot_dir / "sql_concentration_review.csv"),
    }


def score_column(df: pd.DataFrame) -> str | None:
    """Return the dashboard score column if present."""
    for column in ["narrative_momentum_score", "momentum_score"]:
        if column in df.columns:
            return column
    return None


def format_pct(value: object) -> str:
    """Format a percentage-like value."""
    if pd.isna(value):
        return "N/A"
    return f"{float(value):,.2f}%"


def format_ratio_pct(value: object) -> str:
    """Format a 0-1 ratio as a percentage."""
    if pd.isna(value):
        return "N/A"
    return f"{float(value) * 100:,.1f}%"


def format_large_number(value: object) -> str:
    """Format large numeric values for dashboard display."""
    if pd.isna(value):
        return "N/A"
    value = float(value)
    abs_value = abs(value)
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    if abs_value >= 1_000:
        return f"${value / 1_000:,.2f}K"
    return f"${value:,.2f}"


def format_score(value: object) -> str:
    """Format a score from 0 to 100."""
    if pd.isna(value):
        return "N/A"
    return f"{float(value):,.1f}"


def filter_by_narrative(df: pd.DataFrame | None, narrative: str) -> pd.DataFrame | None:
    """Apply a primary narrative filter when available."""
    if df is None or narrative == "All" or "primary_narrative" not in df.columns:
        return df
    return df[df["primary_narrative"] == narrative].copy()


def apply_top_n(df: pd.DataFrame, top_n: str, score_col: str | None) -> pd.DataFrame:
    """Apply a top-N filter to a ranking dataframe."""
    if top_n == "All":
        return df
    if score_col:
        df = df.sort_values(score_col, ascending=False)
    return df.head(int(top_n))


def display_kpis(ranking_df: pd.DataFrame) -> None:
    """Display top-level dashboard KPIs."""
    score_col = score_column(ranking_df)
    columns = st.columns(4)

    if score_col:
        top_row = ranking_df.sort_values(score_col, ascending=False).iloc[0]
        weakest_row = ranking_df.sort_values(score_col, ascending=True).iloc[0]
        columns[0].metric(
            "Top Narrative",
            top_row["primary_narrative"],
            format_score(top_row[score_col]),
        )
        columns[3].metric(
            "Lowest Momentum",
            weakest_row["primary_narrative"],
            format_score(weakest_row[score_col]),
        )
    else:
        columns[0].metric("Top Narrative", "N/A")
        columns[3].metric("Lowest Momentum", "N/A")

    if "avg_return_7d" in ranking_df.columns:
        strongest_7d = ranking_df.sort_values("avg_return_7d", ascending=False).iloc[0]
        columns[1].metric(
            "Strongest 7D Return",
            strongest_7d["primary_narrative"],
            format_pct(strongest_7d["avg_return_7d"]),
        )
    else:
        columns[1].metric("Strongest 7D Return", "N/A")

    breadth_col = "positive_breadth_pct" if "positive_breadth_pct" in ranking_df.columns else "breadth_7d"
    if breadth_col in ranking_df.columns:
        breadth_row = ranking_df.sort_values(breadth_col, ascending=False).iloc[0]
        columns[2].metric(
            "Highest Breadth",
            breadth_row["primary_narrative"],
            format_ratio_pct(breadth_row[breadth_col]),
        )
    else:
        columns[2].metric("Highest Breadth", "N/A")


def select_table_columns(df: pd.DataFrame, preferred_columns: list[str]) -> pd.DataFrame:
    """Return a table with useful columns that exist."""
    columns = [column for column in preferred_columns if column in df.columns]
    return df[columns].copy()


def style_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Apply readable table formatting."""
    formatters = {}
    for column in df.columns:
        if column.endswith("_score"):
            formatters[column] = format_score
        elif "share" in column or column.startswith("breadth"):
            formatters[column] = format_ratio_pct
        elif "return" in column or "percentage" in column:
            formatters[column] = format_pct
        elif column in {"market_cap", "total_market_cap", "total_volume", "top_1_market_cap", "top_3_market_cap", "top_1_volume", "top_3_volume"}:
            formatters[column] = format_large_number
    return df.style.format(formatters)


def main() -> None:
    """Render the Streamlit dashboard."""
    st.set_page_config(page_title="Crypto Narrative Radar", layout="wide")

    st.title("Crypto Narrative Radar")
    st.caption(
        "A market intelligence dashboard for tracking crypto narrative momentum "
        "using CoinGecko market data."
    )

    available_dates = find_processed_snapshots()
    if not available_dates:
        st.error("No processed snapshots found. Run `python scripts/run_daily_pipeline.py` first.")
        return

    with st.sidebar:
        st.header("Filters")
        selected_date = st.selectbox("Snapshot date", available_dates, index=0)

    data = load_snapshot_data(selected_date)
    ranking_df = data["ranking"]
    if ranking_df is None or ranking_df.empty:
        st.error("Required narrative_ranking.csv is missing or empty for this snapshot.")
        return

    st.write(f"Snapshot date: `{selected_date}`")
    st.info(
        "Market intelligence only. This dashboard is not investment advice, "
        "does not predict prices, and does not provide buy/sell signals."
    )

    narratives = sorted(ranking_df["primary_narrative"].dropna().unique().tolist())
    contributor_df = data["contributors"] if data["contributors"] is not None else data["token_snapshot"]
    contributor_sort_options = [
        column
        for column in [
            "total_volume",
            "market_cap",
            "price_change_percentage_24h",
            "price_change_percentage_7d_in_currency",
            "price_change_percentage_30d_in_currency",
            "volume_share_within_narrative",
            "market_cap_share_within_narrative",
        ]
        if contributor_df is not None and column in contributor_df.columns
    ]

    with st.sidebar:
        selected_narrative = st.selectbox("Narrative", ["All"] + narratives)
        top_n = st.selectbox("Top narratives", ["5", "8", "10", "All"], index=1)
        sort_metric = st.selectbox(
            "Token contributor sort metric",
            contributor_sort_options or ["N/A"],
        )

    filtered_ranking = filter_by_narrative(ranking_df, selected_narrative)
    score_col = score_column(filtered_ranking)
    if score_col:
        filtered_ranking = filtered_ranking.sort_values(score_col, ascending=False)
    filtered_ranking = apply_top_n(filtered_ranking, top_n, score_col)

    display_kpis(ranking_df)

    st.subheader("Narrative Ranking")
    ranking_columns = [
        "rank",
        "primary_narrative",
        "narrative_momentum_score",
        "avg_return_7d",
        "avg_return_30d",
        "relative_strength_7d",
        "avg_volume_to_market_cap",
        "breadth_7d",
        "token_count",
        "concentration_flag",
        "scoring_note",
    ]
    ranking_table = select_table_columns(filtered_ranking, ranking_columns)
    st.dataframe(style_table(ranking_table), width="stretch", hide_index=True)

    st.subheader("Narrative Momentum Score")
    if score_col:
        chart_df = filtered_ranking.sort_values(score_col, ascending=True)
        fig = px.bar(
            chart_df,
            x=score_col,
            y="primary_narrative",
            orientation="h",
            title="Narrative Momentum Score",
            labels={score_col: "Score", "primary_narrative": "Narrative"},
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Momentum score column is unavailable.")

    st.subheader("7D vs 30D Average Return by Narrative")
    if {"avg_return_7d", "avg_return_30d", "primary_narrative"} <= set(filtered_ranking.columns):
        returns_df = filtered_ranking.melt(
            id_vars="primary_narrative",
            value_vars=["avg_return_7d", "avg_return_30d"],
            var_name="window",
            value_name="average_return",
        )
        fig = px.bar(
            returns_df,
            x="primary_narrative",
            y="average_return",
            color="window",
            barmode="group",
            title="7D vs 30D Average Return by Narrative",
            labels={"average_return": "Average return (%)", "primary_narrative": "Narrative"},
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("7D and 30D average return columns are unavailable.")

    st.subheader("Return vs Volume Confirmation")
    if {"avg_return_7d", "total_volume", "token_count", "primary_narrative"} <= set(filtered_ranking.columns):
        fig = px.scatter(
            filtered_ranking,
            x="avg_return_7d",
            y="total_volume",
            size="token_count",
            color="primary_narrative",
            title="Return vs Volume Confirmation",
            labels={
                "avg_return_7d": "Average 7D return (%)",
                "total_volume": "Total volume",
                "primary_narrative": "Narrative",
            },
        )
        st.caption("This chart provides market context for research support.")
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Return, volume, or token count columns are unavailable.")

    st.subheader("Token Contributors")
    if data["contributors"] is None:
        st.warning("SQL contributor output is unavailable. Falling back to token market snapshot.")
    if contributor_df is None or contributor_df.empty:
        st.warning("Token contributor data is unavailable.")
    else:
        contributor_view = filter_by_narrative(contributor_df, selected_narrative)
        if sort_metric != "N/A" and sort_metric in contributor_view.columns:
            contributor_view = contributor_view.sort_values(sort_metric, ascending=False)
        contributor_columns = [
            "primary_narrative",
            "symbol",
            "name",
            "coingecko_id",
            "market_cap",
            "total_volume",
            "price_change_percentage_24h",
            "price_change_percentage_7d_in_currency",
            "price_change_percentage_30d_in_currency",
            "volume_share_within_narrative",
            "market_cap_share_within_narrative",
            "volume_rank_within_narrative",
            "market_cap_rank_within_narrative",
        ]
        contributor_table = select_table_columns(contributor_view, contributor_columns)
        st.dataframe(style_table(contributor_table), width="stretch", hide_index=True)

    st.subheader("Concentration Review")
    concentration_df = filter_by_narrative(data["concentration"], selected_narrative)
    st.caption(
        "Concentration review helps show whether narrative-level metrics are broad "
        "or driven by a small number of large tokens."
    )
    if concentration_df is None or concentration_df.empty:
        st.warning("SQL concentration review output is unavailable.")
    else:
        concentration_columns = [
            "primary_narrative",
            "token_count",
            "total_market_cap",
            "top_1_market_cap_share",
            "top_3_market_cap_share",
            "total_volume",
            "top_1_volume_share",
            "top_3_volume_share",
            "concentration_comment",
        ]
        concentration_table = select_table_columns(concentration_df, concentration_columns)
        st.dataframe(style_table(concentration_table), use_container_width=True, hide_index=True)

    with st.expander("Methodology"):
        st.markdown(
            """
            **Narrative taxonomy:** Tokens are grouped into one primary narrative to avoid
            double-counting, while secondary narratives preserve research context.

            **CoinGecko market data:** The dashboard uses market data such as price returns,
            market cap, volume, and last updated timestamps.

            **Narrative-level aggregation:** Token-level data is grouped by
            `primary_narrative`.

            **Momentum score:** The Narrative Momentum Score is a descriptive score combining
            price momentum, relative strength, volume confirmation, and breadth.

            **Breadth:** Breadth shows how widely participation is distributed across tokens
            within a narrative.

            **Volume confirmation:** Volume confirmation helps evaluate whether narrative
            movement is supported by trading activity.

            **Concentration review:** Concentration review shows whether a narrative is
            dominated by a small number of tokens.

            **Limitation:** The dashboard is descriptive, not predictive. It does not provide
            investment advice, trading signals, or price forecasts.
            """
        )


if __name__ == "__main__":
    main()
