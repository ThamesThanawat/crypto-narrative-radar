"""Streamlit dashboard for Crypto Narrative Radar."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
HISTORICAL_NARRATIVE_PATH = (
    PROCESSED_DATA_DIR / "historical" / "narrative_market_history_90d.csv"
)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

DISPLAY_COLUMN_LABELS = {
    "rank": "Rank",
    "primary_narrative": "Narrative",
    "narrative_momentum_score": "Momentum Score",
    "avg_return_7d": "Avg 7D Return",
    "avg_return_30d": "Avg 30D Return",
    "relative_strength_7d": "Benchmark-Relative Strength",
    "avg_volume_to_market_cap": "Volume / Market Cap",
    "breadth_7d": "7D Participation Breadth",
    "token_count": "Token Count",
    "concentration_flag": "Concentration",
    "symbol": "Symbol",
    "name": "Name",
    "coingecko_id": "CoinGecko ID",
    "market_cap": "Market Cap",
    "total_market_cap": "Total Market Cap",
    "total_volume": "Total Volume",
    "price_change_percentage_24h": "24H Return",
    "price_change_percentage_7d_in_currency": "7D Return",
    "price_change_percentage_30d_in_currency": "30D Return",
    "volume_share_within_narrative": "Volume Share",
    "market_cap_share_within_narrative": "Market Cap Share",
    "volume_rank_within_narrative": "Volume Rank",
    "market_cap_rank_within_narrative": "Market Cap Rank",
    "top_1_market_cap_share": "Top Token Market Cap Share",
    "top_3_market_cap_share": "Top 3 Market Cap Share",
    "top_1_volume_share": "Top Token Volume Share",
    "top_3_volume_share": "Top 3 Volume Share",
    "concentration_comment": "Concentration Comment",
    "avg_return_1d": "Avg 1D Return",
    "median_return_1d": "Median 1D Return",
    "median_return_7d": "Median 7D Return",
    "median_return_30d": "Median 30D Return",
    "total_market_cap_usd": "Total Market Cap",
    "total_volume_usd": "Total Volume",
    "breadth_1d": "1D Participation Breadth",
    "breadth_30d": "30D Participation Breadth",
    "rs_vs_btc_7d": "Relative Strength vs BTC",
    "rs_vs_eth_7d": "Relative Strength vs ETH",
}


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


def load_historical_narrative_data(
    path: Path = HISTORICAL_NARRATIVE_PATH,
) -> pd.DataFrame | None:
    """Load historical narrative metrics if the CSV exists."""
    if not path.exists():
        return None
    historical_df = pd.read_csv(path)
    if "date" in historical_df.columns:
        historical_df["date"] = pd.to_datetime(historical_df["date"], errors="coerce")
    return historical_df


def validate_historical_data(df: pd.DataFrame | None) -> list[str]:
    """Return validation warnings for historical narrative data."""
    if df is None:
        return [f"Historical narrative data file not found: {HISTORICAL_NARRATIVE_PATH}"]
    missing_columns = [
        column for column in ["date", "primary_narrative"] if column not in df.columns
    ]
    if missing_columns:
        return [
            "Historical narrative data is missing required column(s): "
            + ", ".join(missing_columns)
        ]
    if df["date"].isna().any():
        return ["Historical narrative data contains invalid date values."]
    if df.empty:
        return ["Historical narrative data is empty."]
    return []


def filter_historical_data(
    df: pd.DataFrame,
    selected_narratives: list[str],
    date_range: object,
) -> pd.DataFrame:
    """Filter historical narrative data by narrative and date range."""
    filtered = df.copy()
    if selected_narratives:
        filtered = filtered[filtered["primary_narrative"].isin(selected_narratives)]

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        filtered = filtered[
            (filtered["date"] >= start_date) & (filtered["date"] <= end_date)
        ]
    return filtered.copy()


def choose_return_metric(df: pd.DataFrame) -> str | None:
    """Choose the preferred historical return metric."""
    for column in ["avg_return_7d", "avg_return_30d"]:
        if column in df.columns:
            return column
    return None


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
        leadership_row = ranking_df.sort_values(score_col, ascending=False).iloc[0]
        columns[0].metric(
            "Narrative Leadership",
            leadership_row["primary_narrative"],
            f"Score {format_score(leadership_row[score_col])}",
        )
    else:
        columns[0].metric("Narrative Leadership", "N/A")

    if "relative_strength_7d" in ranking_df.columns:
        relative_strength_row = ranking_df.sort_values("relative_strength_7d", ascending=False).iloc[0]
        columns[1].metric(
            "Benchmark-Relative Strength",
            relative_strength_row["primary_narrative"],
            format_pct(relative_strength_row["relative_strength_7d"]),
        )
    else:
        columns[1].metric("Benchmark-Relative Strength", "N/A")

    breadth_col = "positive_breadth_pct" if "positive_breadth_pct" in ranking_df.columns else "breadth_7d"
    if breadth_col in ranking_df.columns:
        breadth_row = ranking_df.sort_values(breadth_col, ascending=False).iloc[0]
        columns[2].metric(
            "Participation Breadth",
            breadth_row["primary_narrative"],
            format_ratio_pct(breadth_row[breadth_col]),
        )
    else:
        columns[2].metric("Participation Breadth", "N/A")

    if "top_token_market_cap_share" in ranking_df.columns:
        concentration_row = ranking_df.sort_values(
            "top_token_market_cap_share", ascending=False
        ).iloc[0]
        columns[3].metric(
            "Concentration Watch",
            concentration_row["primary_narrative"],
        )
        columns[3].caption(
            f"Top token share: {format_ratio_pct(concentration_row['top_token_market_cap_share'])}"
        )
    elif score_col:
        weakest_row = ranking_df.sort_values(score_col, ascending=True).iloc[0]
        columns[3].metric(
            "Lowest Momentum",
            weakest_row["primary_narrative"],
            f"Score {format_score(weakest_row[score_col])}",
        )
    else:
        columns[3].metric("Concentration Watch", "N/A")


def select_table_columns(df: pd.DataFrame, preferred_columns: list[str]) -> pd.DataFrame:
    """Return a table with useful columns that exist."""
    columns = [column for column in preferred_columns if column in df.columns]
    return df[columns].copy()


def rename_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Apply human-readable labels for Streamlit display tables."""
    return df.rename(columns=DISPLAY_COLUMN_LABELS)


def style_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Apply readable table formatting."""
    formatters = {}
    for column in df.columns:
        if column.endswith("_score") or column == "Momentum Score":
            formatters[column] = format_score
        elif (
            "share" in column
            or "Share" in column
            or column.startswith("breadth")
            or "Participation Breadth" in column
            or column == "Volume / Market Cap"
        ):
            formatters[column] = format_ratio_pct
        elif (
            "return" in column
            or "Return" in column
            or "percentage" in column
            or column == "Benchmark-Relative Strength"
        ):
            formatters[column] = format_pct
        elif column in {
            "market_cap",
            "total_market_cap",
            "total_volume",
            "top_1_market_cap",
            "top_3_market_cap",
            "top_1_volume",
            "top_3_volume",
            "total_market_cap_usd",
            "total_volume_usd",
            "Total Market Cap",
            "Total Volume",
            "Market Cap",
            "Total Market Cap",
            "Total Volume",
        }:
            formatters[column] = format_large_number
    return df.style.format(formatters)


def _line_chart(
    df: pd.DataFrame,
    y_column: str,
    title: str,
    y_label: str,
) -> None:
    fig = px.line(
        df.sort_values("date"),
        x="date",
        y=y_column,
        color="primary_narrative",
        title=title,
        labels={
            "date": "Date",
            y_column: y_label,
            "primary_narrative": "Narrative",
        },
    )
    st.plotly_chart(fig, width="stretch")


def render_historical_narrative_trends() -> None:
    """Render the historical narrative trends dashboard section."""
    st.header("Historical Narrative Trends")
    st.caption(
        "Historical Narrative Trends provides a descriptive view of how "
        "narrative-level market metrics evolved over the available historical "
        "window. It is intended for research context and market intelligence."
    )

    historical_df = load_historical_narrative_data()
    warnings = validate_historical_data(historical_df)
    if warnings:
        for warning in warnings:
            st.warning(warning)
        return

    assert historical_df is not None
    narratives = sorted(historical_df["primary_narrative"].dropna().unique().tolist())
    min_date = historical_df["date"].min().date()
    max_date = historical_df["date"].max().date()

    filter_columns = st.columns([2, 1])
    selected_narratives = filter_columns[0].multiselect(
        "Historical narratives",
        narratives,
        default=narratives,
    )
    selected_date_range = filter_columns[1].date_input(
        "Historical date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    filtered_history = filter_historical_data(
        historical_df,
        selected_narratives,
        selected_date_range,
    )
    if filtered_history.empty:
        st.warning("No historical narrative rows match the selected filters.")
        return

    return_metric = choose_return_metric(filtered_history)
    st.subheader("Historical Narrative Return Trend")
    st.caption(
        "Tracks how average narrative-level returns evolved over time across "
        "selected narratives."
    )
    if return_metric:
        _line_chart(
            filtered_history,
            return_metric,
            "Historical Narrative Return Trend",
            DISPLAY_COLUMN_LABELS.get(return_metric, return_metric),
        )
    else:
        st.warning(
            "Historical return columns are unavailable. Expected avg_return_7d "
            "or avg_return_30d."
        )

    st.subheader("Breadth of Participation Over Time")
    st.caption(
        "Shows the share of tokens within each narrative with positive performance."
    )
    breadth_column = next(
        (
            column
            for column in ["positive_breadth_pct", "breadth_7d"]
            if column in filtered_history.columns
        ),
        None,
    )
    if breadth_column:
        _line_chart(
            filtered_history,
            breadth_column,
            "Breadth of Participation Over Time",
            DISPLAY_COLUMN_LABELS.get(breadth_column, breadth_column),
        )
    else:
        st.info(
            "Historical breadth columns are unavailable, so the breadth view is skipped."
        )

    st.subheader("Relative Strength vs BTC/ETH")
    st.caption(
        "Compares narrative-level performance against BTC or ETH as major crypto "
        "benchmarks."
    )
    benchmark_columns = {
        "BTC": next(
            (
                column
                for column in ["btc_relative_strength_7d", "rs_vs_btc_7d"]
                if column in filtered_history.columns
            ),
            None,
        ),
        "ETH": next(
            (
                column
                for column in ["eth_relative_strength_7d", "rs_vs_eth_7d"]
                if column in filtered_history.columns
            ),
            None,
        ),
    }
    available_benchmarks = {
        label: column for label, column in benchmark_columns.items() if column
    }
    if available_benchmarks:
        if len(available_benchmarks) > 1:
            selected_benchmark = st.selectbox(
                "Relative strength benchmark",
                list(available_benchmarks),
            )
        else:
            selected_benchmark = next(iter(available_benchmarks))
        relative_strength_column = available_benchmarks[selected_benchmark]
        _line_chart(
            filtered_history,
            relative_strength_column,
            "Relative Strength vs BTC/ETH",
            f"Relative Strength vs {selected_benchmark}",
        )
    else:
        st.info(
            "Historical BTC/ETH relative strength columns are unavailable, so this "
            "view is skipped."
        )

    st.subheader("Narrative Concentration Over Time")
    st.caption(
        "Shows whether narrative market cap became more concentrated or broadly "
        "distributed over time."
    )
    concentration_options = [
        column
        for column in ["top_3_market_cap_share", "top_token_market_cap_share"]
        if column in filtered_history.columns
    ]
    if concentration_options:
        default_index = (
            concentration_options.index("top_3_market_cap_share")
            if "top_3_market_cap_share" in concentration_options
            else 0
        )
        concentration_column = st.selectbox(
            "Concentration metric",
            concentration_options,
            index=default_index,
            format_func=lambda column: DISPLAY_COLUMN_LABELS.get(column, column),
        )
        _line_chart(
            filtered_history,
            concentration_column,
            "Narrative Concentration Over Time",
            DISPLAY_COLUMN_LABELS.get(concentration_column, concentration_column),
        )
    else:
        st.info(
            "Historical concentration columns are unavailable, so the concentration "
            "context view is skipped."
        )

    st.subheader("Market Activity Over Time")
    st.caption("Shows descriptive market activity context for selected narratives.")
    activity_options = [
        column
        for column in [
            "total_volume",
            "total_volume_usd",
            "total_market_cap",
            "total_market_cap_usd",
        ]
        if column in filtered_history.columns
    ]
    if activity_options:
        activity_column = st.selectbox(
            "Market activity metric",
            activity_options,
            format_func=lambda column: DISPLAY_COLUMN_LABELS.get(column, column),
        )
        _line_chart(
            filtered_history,
            activity_column,
            "Market Activity Over Time",
            DISPLAY_COLUMN_LABELS.get(activity_column, activity_column),
        )
    else:
        st.info(
            "Historical market activity columns are unavailable, so this context "
            "view is skipped."
        )


def main() -> None:
    """Render the Streamlit dashboard."""
    st.set_page_config(page_title="Crypto Narrative Radar", layout="wide")

    st.title("Crypto Narrative Radar")
    st.caption(
        "Market intelligence for crypto sector rotation, narrative leadership, "
        "benchmark-relative strength, volume confirmation, and participation breadth."
    )

    available_dates = find_processed_snapshots()
    if not available_dates:
        st.error("No processed snapshots found. Run `python scripts/run_daily_pipeline.py` first.")
        return

    with st.sidebar:
        st.header("Research Filters")
        selected_date = st.selectbox("Snapshot date", available_dates, index=0)

    data = load_snapshot_data(selected_date)
    ranking_df = data["ranking"]
    if ranking_df is None or ranking_df.empty:
        st.error("Required narrative_ranking.csv is missing or empty for this snapshot.")
        return

    st.write(f"Snapshot date: `{selected_date}`")
    st.info(
        "Research support only. This dashboard describes market structure and relative "
        "narrative conditions; it is not investment advice or a recommendation tool."
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
            "Token contributor lens",
            contributor_sort_options or ["N/A"],
        )

    filtered_ranking = filter_by_narrative(ranking_df, selected_narrative)
    score_col = score_column(filtered_ranking)
    if score_col:
        filtered_ranking = filtered_ranking.sort_values(score_col, ascending=False)
    filtered_ranking = apply_top_n(filtered_ranking, top_n, score_col)

    display_kpis(ranking_df)

    st.subheader("Narrative Leadership Table")
    st.caption(
        "What is happening: narratives are ranked by the descriptive Narrative Momentum "
        "Score, with returns, benchmark-relative strength, volume confirmation, breadth, "
        "and concentration shown side by side."
    )
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
    ]
    ranking_table = select_table_columns(filtered_ranking, ranking_columns)
    st.dataframe(
        style_table(rename_for_display(ranking_table)),
        width="stretch",
        hide_index=True,
    )

    st.subheader("Narrative Momentum Score by Sector")
    st.caption(
        "A higher score indicates stronger recent narrative momentum across price action, "
        "relative strength, volume confirmation, and participation breadth."
    )
    if score_col:
        chart_df = filtered_ranking.sort_values(score_col, ascending=True)
        fig = px.bar(
            chart_df,
            x=score_col,
            y="primary_narrative",
            orientation="h",
            title="Narrative Momentum Score by Sector",
            labels={score_col: "Research score", "primary_narrative": "Narrative"},
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Momentum score column is unavailable.")

    st.subheader("7D vs 30D Sector Rotation")
    st.caption(
        "Why it may be happening: comparing recent and medium-term returns helps "
        "separate fresh leadership from narratives that are cooling or still recovering."
    )
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
    st.caption(
        "What to validate next: stronger return profiles are more useful for research when "
        "they are supported by meaningful trading volume. The volume axis uses a log scale "
        "so large-cap narratives do not compress the rest of the market map."
    )
    if {"avg_return_7d", "total_volume", "token_count", "primary_narrative"} <= set(filtered_ranking.columns):
        fig = px.scatter(
            filtered_ranking,
            x="avg_return_7d",
            y="total_volume",
            size="token_count",
            color="primary_narrative",
            title="7D Return vs Volume Confirmation",
            labels={
                "avg_return_7d": "Average 7D return (%)",
                "total_volume": "Total volume",
                "primary_narrative": "Narrative",
            },
            log_y=True,
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Return, volume, or token count columns are unavailable.")

    st.subheader("Token Contributors: What Is Driving the Move?")
    st.caption(
        "Token contributors help identify whether narrative leadership is being driven by "
        "large-cap constituents, high-volume tokens, or broader participation across the basket."
    )
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
        st.dataframe(
            style_table(rename_for_display(contributor_table)),
            width="stretch",
            hide_index=True,
        )

    st.subheader("Concentration Review: Broad vs Concentrated Participation")
    concentration_df = filter_by_narrative(data["concentration"], selected_narrative)
    st.caption(
        "Concentration review shows whether narrative-level market cap and volume are "
        "distributed across the basket or dominated by a small number of token contributors."
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
        st.dataframe(
            style_table(rename_for_display(concentration_table)),
            width="stretch",
            hide_index=True,
        )

    render_historical_narrative_trends()

    with st.expander("Methodology and Interpretation Guide"):
        st.markdown(
            """
            **Narrative taxonomy:** Tokens are grouped into one primary narrative so sector
            rotation can be compared without double-counting. Secondary narratives preserve
            research context for tokens that span multiple themes.

            **Market snapshot:** CoinGecko market data provides point-in-time returns,
            market cap, trading volume, and last updated timestamps for the curated token universe.

            **Narrative-level aggregation:** Token-level observations are grouped by
            `primary_narrative` to create a sector-level research view.

            **Narrative Momentum Score:** The score is a descriptive research ranking from
            0 to 100. It combines price momentum, benchmark-relative strength, volume
            confirmation, and participation breadth. It helps compare current narrative
            leadership across sectors. The current snapshot uses the full V1 scoring weights
            when BTC and ETH benchmark data is available.

            **Benchmark-relative strength:** Relative strength compares narrative performance
            against BTC and ETH over the selected window. It helps distinguish sector-specific
            leadership from broad crypto market movement.

            **Volume confirmation:** Volume confirmation uses trading activity as a liquidity
            and attention proxy. Higher confirmation suggests the move is supported by market
            activity, but it is not proof of fundamental adoption.

            **Participation breadth:** Breadth measures the share of tokens in a narrative
            with positive returns. Broad participation is generally more informative than a
            move concentrated in one or two constituents.

            **Concentration review:** Concentration review shows whether market cap or volume
            is dominated by a small number of token contributors. It is used for interpretation
            and is separate from the Narrative Momentum Score.

            **Research use:** The dashboard is descriptive market intelligence. It is designed
            to help identify what is happening, why a narrative may be leading or lagging, and
            which token contributors may warrant deeper review.
            """
        )


if __name__ == "__main__":
    main()
