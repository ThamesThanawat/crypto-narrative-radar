from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from crypto_narrative_radar.reports.html_report import (
    calculate_return_skew_diagnostics,
    collect_report_qa_warnings,
    detect_score_column,
    find_latest_processed_date,
    format_percent_point,
    format_ratio_pct,
    format_value,
    generate_report,
    load_required_csv,
    prepare_executive_summary,
    prepare_report_context,
    render_report,
)


def base_ranking_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rank": 1,
                "primary_narrative": "AI",
                "narrative_momentum_score": 88,
                "avg_return_7d": 4,
                "median_return_7d": 3,
                "avg_return_30d": 12,
                "breadth_7d": 0.75,
                "total_market_cap": 1000,
                "total_volume": 100,
                "relative_strength_7d": 2,
                "concentration_flag": "Medium",
            }
        ]
    )


def base_token_snapshot_df(**overrides: object) -> pd.DataFrame:
    row = {
        "coingecko_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "current_price": 100,
        "market_cap": 1000,
        "total_volume": 100,
        "price_change_percentage_24h": 1,
        "price_change_percentage_7d_in_currency": 4,
        "price_change_percentage_30d_in_currency": 12,
        "last_updated": "2026-05-25T00:00:00Z",
        "primary_narrative": "AI",
    }
    row.update(overrides)
    return pd.DataFrame([row])


def write_ranking(path: Path, score_column: str = "narrative_momentum_score") -> None:
    df = pd.DataFrame(
        [
            {
                "rank": 1,
                "primary_narrative": "AI",
                "token_count": 10,
                score_column: 92,
                "avg_return_7d": 12,
                "median_return_7d": 10,
                "avg_return_30d": 20,
                "breadth_7d": 0.8,
                "total_market_cap": 1000,
                "total_volume": 100,
                "relative_strength_7d": 8,
                "concentration_flag": "Medium",
                "price_momentum_score": 100,
                "relative_strength_score": 100,
                "volume_confirmation_score": 80,
                "breadth_score": 90,
                "scoring_note": "Full V1 scoring weights applied.",
            },
            {
                "rank": 2,
                "primary_narrative": "Layer 1",
                "token_count": 10,
                score_column: 75,
                "avg_return_7d": 7,
                "median_return_7d": 6,
                "avg_return_30d": 12,
                "breadth_7d": 0.7,
                "total_market_cap": 950,
                "total_volume": 95,
                "relative_strength_7d": 4,
                "concentration_flag": "High",
                "price_momentum_score": 80,
                "relative_strength_score": 75,
                "volume_confirmation_score": 60,
                "breadth_score": 70,
                "scoring_note": "Full V1 scoring weights applied.",
            },
            {
                "rank": 3,
                "primary_narrative": "DeFi",
                "token_count": 10,
                score_column: 51,
                "avg_return_7d": 3,
                "median_return_7d": 3,
                "avg_return_30d": 6,
                "breadth_7d": 0.5,
                "total_market_cap": 800,
                "total_volume": 80,
                "relative_strength_7d": 1,
                "concentration_flag": "Low",
                "price_momentum_score": 50,
                "relative_strength_score": 60,
                "volume_confirmation_score": 55,
                "breadth_score": 50,
                "scoring_note": "Full V1 scoring weights applied.",
            },
            {
                "rank": 4,
                "primary_narrative": "RWA",
                "token_count": 10,
                score_column: 35,
                "avg_return_7d": -1,
                "median_return_7d": 0,
                "avg_return_30d": -3,
                "breadth_7d": 0.4,
                "total_market_cap": 600,
                "total_volume": 60,
                "relative_strength_7d": -2,
                "concentration_flag": "Medium",
                "price_momentum_score": 40,
                "relative_strength_score": 40,
                "volume_confirmation_score": 30,
                "breadth_score": 35,
                "scoring_note": "Full V1 scoring weights applied.",
            },
            {
                "rank": 5,
                "primary_narrative": "Gaming / GameFi",
                "token_count": 10,
                score_column: 20,
                "avg_return_7d": -2,
                "median_return_7d": -1,
                "avg_return_30d": -8,
                "breadth_7d": 0.2,
                "total_market_cap": 400,
                "total_volume": 40,
                "relative_strength_7d": -4,
                "concentration_flag": "Medium",
                "price_momentum_score": 20,
                "relative_strength_score": 20,
                "volume_confirmation_score": 20,
                "breadth_score": 20,
                "scoring_note": "Full V1 scoring weights applied.",
            },
        ]
    )
    df.to_csv(path, index=False)


def skew_token_snapshot_df() -> pd.DataFrame:
    rows = [
        ("hyperliquid", "HYPE", "Hyperliquid", "AI", 20),
        ("bittensor", "TAO", "Bittensor", "AI", 1),
        ("render-token", "RENDER", "Render", "AI", 2),
        ("near", "NEAR", "NEAR Protocol", "AI", 3),
        ("akash-network", "AKT", "Akash Network", "AI", 4),
        ("ethereum", "ETH", "Ethereum", "Layer 1", 0),
        ("solana", "SOL", "Solana", "Layer 1", 1),
        ("sui", "SUI", "Sui", "Layer 1", 2),
        ("aptos", "APT", "Aptos", "Layer 1", 3),
        ("cardano", "ADA", "Cardano", "Layer 1", 4),
        ("uniswap", "UNI", "Uniswap", "DeFi", 1),
        ("aave", "AAVE", "Aave", "DeFi", 2),
        ("maker", "MKR", "Maker", "DeFi", 3),
        ("curve-dao-token", "CRV", "Curve", "DeFi", 4),
        ("lido-dao", "LDO", "Lido DAO", "DeFi", 5),
        ("chainlink", "LINK", "Chainlink", "RWA", -10),
        ("ondo-finance", "ONDO", "Ondo", "RWA", -9),
        ("maker-rwa", "MKR", "Maker RWA", "RWA", 0),
        ("pendle", "PENDLE", "Pendle", "RWA", 9),
        ("centrifuge", "CFG", "Centrifuge", "RWA", 10),
        ("gala", "GALA", "Gala", "Gaming / GameFi", -20),
        ("immutable-x", "IMX", "Immutable", "Gaming / GameFi", -10),
        ("the-sandbox", "SAND", "The Sandbox", "Gaming / GameFi", 0),
        ("ronin", "RON", "Ronin", "Gaming / GameFi", 10),
        ("axie-infinity", "AXS", "Axie Infinity", "Gaming / GameFi", 40),
    ]
    return pd.DataFrame(
        [
            {
                "coingecko_id": coingecko_id,
                "symbol": symbol,
                "name": name,
                "primary_narrative": narrative,
                "price_change_percentage_7d_in_currency": return_7d,
            }
            for coingecko_id, symbol, name, narrative, return_7d in rows
        ]
    )


def write_token_snapshot(path: Path) -> None:
    skew_token_snapshot_df().to_csv(path, index=False)


def extract_return_skew_section(html: str) -> str:
    start = html.index("<h2>Return Skew Diagnostics</h2>")
    end = html.index("<h2>Return, Volume, and Breadth Review</h2>", start)
    return html[start:end]


def test_report_qa_warns_for_stale_snapshot_data() -> None:
    warnings = collect_report_qa_warnings(
        "2026-05-25",
        ranking_df=base_ranking_df(),
        token_snapshot_df=base_token_snapshot_df(last_updated="2026-05-20T00:00:00Z"),
        generated_at=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )

    assert any("stale" in warning.lower() for warning in warnings)


def test_report_qa_warns_for_duplicate_token_ids() -> None:
    token_snapshot = pd.concat(
        [
            base_token_snapshot_df(),
            base_token_snapshot_df(symbol="ETH", name="Ethereum"),
        ],
        ignore_index=True,
    )

    warnings = collect_report_qa_warnings(
        "2026-05-25",
        ranking_df=base_ranking_df(),
        token_snapshot_df=token_snapshot,
        generated_at=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )

    assert any("duplicate coingecko id" in warning.lower() for warning in warnings)


def test_report_qa_warns_for_missing_and_nonpositive_price() -> None:
    token_snapshot = pd.concat(
        [
            base_token_snapshot_df(current_price=pd.NA),
            base_token_snapshot_df(coingecko_id="ethereum", symbol="ETH", current_price=0),
        ],
        ignore_index=True,
    )

    warnings = collect_report_qa_warnings(
        "2026-05-25",
        ranking_df=base_ranking_df(),
        token_snapshot_df=token_snapshot,
        generated_at=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )

    assert any("missing or unparseable price" in warning.lower() for warning in warnings)
    assert any("nonpositive price" in warning.lower() for warning in warnings)


def test_report_qa_warns_for_extreme_current_percent_point_returns() -> None:
    warnings = collect_report_qa_warnings(
        "2026-05-25",
        ranking_df=base_ranking_df(),
        token_snapshot_df=base_token_snapshot_df(
            price_change_percentage_7d_in_currency=125
        ),
        generated_at=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )

    assert any("above 100% absolute" in warning for warning in warnings)


def test_latest_processed_date_detection_chooses_latest_date_folder(tmp_path: Path) -> None:
    (tmp_path / "2026-05-23").mkdir()
    (tmp_path / "historical").mkdir()
    (tmp_path / "2026-05-25").mkdir()

    assert find_latest_processed_date(tmp_path) == "2026-05-25"


def test_required_narrative_ranking_missing_raises_clear_error(tmp_path: Path) -> None:
    missing_path = tmp_path / "narrative_ranking.csv"

    with pytest.raises(FileNotFoundError, match="Required report input missing"):
        load_required_csv(missing_path)


def test_optional_files_missing_do_not_fail_context_preparation(tmp_path: Path) -> None:
    processed_dir = tmp_path / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")

    context = prepare_report_context(
        processed_root=tmp_path,
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )

    assert context["snapshot_date"] == "2026-05-25"
    assert context["token_contributor_note"]
    assert context["concentration_note"]
    assert len(context["top_narratives"]["rows"]) == 3
    assert len(context["weakening_narratives"]["rows"]) == 3


def test_score_column_detection_supports_expected_names() -> None:
    assert detect_score_column(pd.DataFrame({"momentum_score": [1]})) == "momentum_score"
    assert (
        detect_score_column(pd.DataFrame({"narrative_momentum_score": [1]}))
        == "narrative_momentum_score"
    )


def test_percent_point_formatter_does_not_rescale_returns() -> None:
    assert format_percent_point(-0.891) == "-0.9%"
    assert format_percent_point(0.947) == "0.9%"
    assert format_percent_point(-0.78) == "-0.8%"


def test_ratio_percentage_formatter_rescales_fractions() -> None:
    assert format_ratio_pct(0.625) == "62.5%"
    assert format_ratio_pct(1.0) == "100.0%"


def test_percentage_formatters_handle_missing_values() -> None:
    assert format_percent_point(None) == "N/A"
    assert format_percent_point(float("nan")) == "N/A"
    assert format_ratio_pct(None) == "N/A"
    assert format_ratio_pct(float("nan")) == "N/A"


def test_column_based_formatter_uses_explicit_percentage_scales() -> None:
    assert format_value(-0.891, "avg_return_7d") == "-0.9%"
    assert format_value(0.947, "price_change_percentage_7d_in_currency") == "0.9%"
    assert format_value(0.625, "positive_breadth_pct") == "62.5%"
    assert format_value(0.8, "top_3_market_cap_share") == "80.0%"


def test_column_based_formatter_allows_historical_ratio_overrides() -> None:
    assert format_value(0.174, "avg_return_7d", "ratio_pct") == "17.4%"
    assert format_value(0.132, "relative_strength_7d", "ratio_pct") == "13.2%"
    assert format_value(0.90, "breadth_7d", "ratio_pct") == "90.0%"
    assert format_value(0.946, "top_3_market_cap_share") == "94.6%"


def test_return_skew_diagnostics_calculates_mean_median_gap_and_iqr() -> None:
    diagnostics = calculate_return_skew_diagnostics(skew_token_snapshot_df())
    rows = diagnostics.set_index("primary_narrative")

    ai = rows.loc["AI"]
    assert ai["token_count"] == 5
    assert ai["avg_return_7d"] == pytest.approx(6.0)
    assert ai["median_return_7d"] == pytest.approx(3.0)
    assert ai["mean_median_gap_pp"] == pytest.approx(3.0)
    assert ai["return_iqr_7d"] == pytest.approx(2.0)
    assert ai["top_return_symbol"] == "HYPE"
    assert ai["top_return_7d"] == pytest.approx(20.0)
    assert ai["bottom_return_symbol"] == "TAO"
    assert ai["bottom_return_7d"] == pytest.approx(1.0)
    assert ai["median_return_iqr_7d_across_narratives"] == pytest.approx(2.0)

def test_return_skew_review_flags_cover_skew_dispersion_and_combined_triggers() -> None:
    diagnostics = calculate_return_skew_diagnostics(skew_token_snapshot_df())
    rows = diagnostics.set_index("primary_narrative")

    assert rows.loc["AI", "skew_review_flag"] == "Skew Review"
    assert rows.loc["RWA", "skew_review_flag"] == "Dispersion Review"
    assert rows.loc["Gaming / GameFi", "skew_review_flag"] == "Skew + Dispersion Review"
    assert rows.loc["Layer 1", "skew_review_flag"] == "No Review"
    assert rows.loc["AI", "skew_trigger"]
    assert not rows.loc["AI", "dispersion_trigger"]
    assert not rows.loc["RWA", "skew_trigger"]
    assert rows.loc["RWA", "dispersion_trigger"]
    assert rows.loc["Gaming / GameFi", "skew_trigger"]
    assert rows.loc["Gaming / GameFi", "dispersion_trigger"]


def test_return_skew_diagnostic_notes_are_factual() -> None:
    diagnostics = calculate_return_skew_diagnostics(skew_token_snapshot_df())
    rows = diagnostics.set_index("primary_narrative")

    assert (
        rows.loc["AI", "diagnostic_note"]
        == "Mean-median gap was 3.0pp. Top 7D token was HYPE at 20.0%; bottom 7D token was TAO at 1.0%."
    )
    assert (
        rows.loc["RWA", "diagnostic_note"]
        == "7D return IQR was 18.0pp versus snapshot median IQR of 2.0pp. Top 7D token was CFG at 10.0%; bottom 7D token was LINK at -10.0%."
    )
    assert (
        rows.loc["Gaming / GameFi", "diagnostic_note"]
        == "Mean-median gap was 4.0pp and 7D return IQR was 20.0pp versus snapshot median IQR of 2.0pp. Top 7D token was AXS at 40.0%; bottom 7D token was GALA at -20.0%."
    )
    assert (
        rows.loc["Layer 1", "diagnostic_note"]
        == "Mean-median gap was 0.0pp and 7D return IQR was 2.0pp; neither exceeded V1 review thresholds."
    )
    assert "no skew" not in rows.loc["RWA", "diagnostic_note"].lower()
    forbidden_terms = ["risky", "buy", "sell", "signal", "prediction", "alpha"]
    notes = " ".join(diagnostics["diagnostic_note"].str.lower())
    assert not any(term in notes for term in forbidden_terms)


def test_rendered_return_skew_diagnostics_section_and_methodology(tmp_path: Path) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")
    write_token_snapshot(processed_dir / "token_market_snapshot_2026-05-25.csv")

    output_path = generate_report(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    html = output_path.read_text(encoding="utf-8")
    section = extract_return_skew_section(html)

    assert "Return Skew Diagnostics" in section
    assert "does not affect the Narrative Momentum Score" in section
    assert "<th>Mean-Median Gap</th>" in section
    assert "<th>7D Return IQR</th>" in section
    assert "<th>Top 7D Token</th>" in section
    assert "<th>Bottom 7D Token</th>" in section
    assert "<th>Review Flag</th>" in section
    assert "HYPE (20.0%)" in section
    assert "LINK (-10.0%)" in section
    assert "3.0pp" in section
    assert "The IQR threshold is snapshot-relative" in html
    assert "not an absolute cross-date threshold" in html
    assert "judgment-based V1 review heuristics, not statistically derived cutoffs" in html
    assert "does not imply an investment recommendation" in html


def test_narrative_ranking_includes_median_7d_return(tmp_path: Path) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")

    output_path = generate_report(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    html = output_path.read_text(encoding="utf-8")
    ranking_start = html.index("<h2>Narrative Ranking</h2>")
    ranking_end = html.index("<h2>Score Component Breakdown</h2>", ranking_start)
    ranking_section = html[ranking_start:ranking_end]

    assert "<th>Mean 7D Return</th>" in ranking_section
    assert "<th>Median 7D Return</th>" in ranking_section


def test_return_skew_diagnostics_do_not_add_return_contribution_share(
    tmp_path: Path,
) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")
    write_token_snapshot(processed_dir / "token_market_snapshot_2026-05-25.csv")

    context = prepare_report_context(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    table = context["return_skew_diagnostics"]
    assert table is not None
    assert not any("return_contribution" in column for column in table["columns"])

    output_path = render_report(context, templates_root=Path("templates"))
    html = output_path.read_text(encoding="utf-8").lower()
    assert "return contribution share" not in html
    assert "return_contribution" not in html


def test_return_skew_section_avoids_trading_prediction_and_backtesting_language(
    tmp_path: Path,
) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")
    write_token_snapshot(processed_dir / "token_market_snapshot_2026-05-25.csv")

    output_path = generate_report(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    html = output_path.read_text(encoding="utf-8")
    section = extract_return_skew_section(html).lower()

    forbidden_terms = ["trading", "prediction", "backtesting", "buy/sell", "signal", "alpha"]
    assert not any(term in section for term in forbidden_terms)


def test_executive_summary_identifies_top_and_weakest_narratives() -> None:
    ranking = pd.DataFrame(
        {
            "primary_narrative": ["AI", "DeFi", "RWA"],
            "narrative_momentum_score": [90, 40, 65],
            "avg_return_7d": [8, -3, 4],
            "avg_return_30d": [10, -4, 9],
            "breadth_7d": [0.9, 0.2, 0.6],
        }
    )

    summary = prepare_executive_summary(ranking)

    assert summary["top_score"]["primary_narrative"] == "AI"
    assert summary["weakest_score"]["primary_narrative"] == "DeFi"


def test_render_report_creates_dated_report_and_latest(tmp_path: Path) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")

    output_path = generate_report(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    latest_path = tmp_path / "reports" / "html" / "latest.html"
    html = output_path.read_text(encoding="utf-8")

    assert output_path.name == "crypto_narrative_report_2026-05-25.html"
    assert output_path.exists()
    assert latest_path.exists()
    assert "Executive Summary" in html
    assert "Narrative Ranking" in html
    assert "Methodology" in html
    assert "Limitations" in html


def test_generated_content_avoids_trading_framing(tmp_path: Path) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")

    output_path = generate_report(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    html = output_path.read_text(encoding="utf-8").lower()

    assert "trading signal" not in html
    assert "alpha guarantee" not in html


def test_rendered_report_uses_correct_percentage_scales(tmp_path: Path) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "rank": 1,
                "primary_narrative": "Layer 1",
                "narrative_momentum_score": 80,
                "avg_return_7d": -0.891,
                "avg_return_30d": 2,
                "breadth_7d": 0.625,
                "total_market_cap": 1000,
                "total_volume": 100,
                "relative_strength_7d": -0.5,
            }
        ]
    ).to_csv(processed_dir / "narrative_ranking.csv", index=False)
    pd.DataFrame(
        [
            {
                "primary_narrative": "Layer 1",
                "symbol": "ETH",
                "name": "Ethereum",
                "market_cap": 1000,
                "total_volume": 100,
                "price_change_percentage_7d_in_currency": -0.891,
                "volume_share_within_narrative": 0.625,
                "market_cap_share_within_narrative": 1.0,
            }
        ]
    ).to_csv(processed_dir / "sql_top_token_contributors.csv", index=False)

    output_path = generate_report(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    html = output_path.read_text(encoding="utf-8")

    assert "-0.9%" in html
    assert "-89.1%" not in html
    assert "62.5%" in html


def test_rendered_historical_context_uses_ratio_percentage_scale(tmp_path: Path) -> None:
    processed_root = tmp_path / "processed"
    processed_dir = processed_root / "2026-05-25"
    historical_dir = processed_root / "historical"
    processed_dir.mkdir(parents=True)
    historical_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")
    pd.DataFrame(
        [
            {
                "date": "2026-05-25",
                "primary_narrative": "AI",
                "avg_return_7d": 0.174,
                "median_return_7d": 0.155,
                "avg_return_30d": 0.1119,
                "median_return_30d": 0.101,
                "breadth_7d": 0.90,
                "rs_vs_btc_7d": 0.071,
                "rs_vs_eth_7d": 0.061,
                "rs_vs_btc_30d": 0.041,
                "rs_vs_eth_30d": 0.031,
                "relative_strength_7d": 0.132,
                "relative_strength_30d": 0.1526,
                "total_market_cap_usd": 1000,
                "total_volume_usd": 100,
            }
        ]
    ).to_csv(historical_dir / "narrative_market_history_90d.csv", index=False)

    output_path = generate_report(
        processed_root=processed_root,
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    html = output_path.read_text(encoding="utf-8")

    assert "17.4%" in html
    assert "15.5%" in html
    assert "11.2%" in html
    assert "10.1%" in html
    assert "90.0%" in html
    assert "7.1%" in html
    assert "6.1%" in html
    assert "4.1%" in html
    assert "3.1%" in html
    assert "13.2%" in html
    assert "15.3%" in html
    assert "0.2%" not in html


def test_historical_coverage_warning_does_not_fail_report_generation(
    tmp_path: Path,
) -> None:
    processed_root = tmp_path / "processed"
    processed_dir = processed_root / "2026-05-25"
    historical_dir = processed_root / "historical"
    processed_dir.mkdir(parents=True)
    historical_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "rank": 1,
                "primary_narrative": "AI",
                "narrative_momentum_score": 80,
                "avg_return_7d": 4,
                "avg_return_30d": 10,
                "breadth_7d": 0.8,
                "total_market_cap": 1000,
                "total_volume": 100,
                "relative_strength_7d": 2,
            },
            {
                "rank": 2,
                "primary_narrative": "DeFi",
                "narrative_momentum_score": 60,
                "avg_return_7d": 2,
                "avg_return_30d": 5,
                "breadth_7d": 0.5,
                "total_market_cap": 800,
                "total_volume": 80,
                "relative_strength_7d": 1,
            },
        ]
    ).to_csv(processed_dir / "narrative_ranking.csv", index=False)
    pd.DataFrame(
        [
            {
                "date": "2026-05-25",
                "primary_narrative": "AI",
                "avg_return_7d": 0.1,
                "avg_return_30d": 0.2,
                "breadth_7d": 0.7,
                "relative_strength_7d": 0.05,
                "relative_strength_30d": 0.08,
            }
        ]
    ).to_csv(historical_dir / "narrative_market_history_90d.csv", index=False)

    output_path = generate_report(
        processed_root=processed_root,
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    html = output_path.read_text(encoding="utf-8")

    assert output_path.exists()
    assert "Data Quality Notes" in html
    assert "missing expected narrative(s): DeFi" in html


def test_rendered_report_uses_research_friendly_section_titles_and_headers(
    tmp_path: Path,
) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")

    output_path = generate_report(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    html = output_path.read_text(encoding="utf-8")

    assert "Top 3 by Narrative Momentum Score" in html
    assert "Lowest 3 by Narrative Momentum Score" in html
    assert "Score Component Breakdown" in html
    assert "<th>Narrative</th>" in html
    assert "<th>Mean 7D Return</th>" in html
    assert "<th>Median 7D Return</th>" in html
    assert "<th>Narrative Momentum Score</th>" in html
    assert "<th>Price Momentum Score</th>" in html
    assert "<th>Relative Strength Score</th>" in html
    assert "<th>Volume Confirmation Score</th>" in html
    assert "<th>Breadth Score</th>" in html
    assert "<th>Scoring Note</th>" in html
    assert "Avg RS vs BTC/ETH 7D" in html
    assert "Top 5 by Narrative Momentum Score" not in html
    assert "Lowest 5 by Narrative Momentum Score" not in html
    assert "Top 5 Outperforming Narratives" not in html
    assert "Top 5 Weakening Narratives" not in html


def test_score_component_breakdown_appears_when_component_columns_exist(
    tmp_path: Path,
) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")

    context = prepare_report_context(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )

    component_table = context["score_component_breakdown"]
    assert component_table is not None
    assert component_table["columns"] == [
        "rank",
        "primary_narrative",
        "narrative_momentum_score",
        "price_momentum_score",
        "relative_strength_score",
        "volume_confirmation_score",
        "breadth_score",
        "scoring_note",
    ]
    assert component_table["labels"]["price_momentum_score"] == "Price Momentum Score"
    assert component_table["labels"]["volume_confirmation_score"] == "Volume Confirmation Score"


def test_methodology_explains_score_interpretation_and_limitations(
    tmp_path: Path,
) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")

    output_path = generate_report(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    html = output_path.read_text(encoding="utf-8")

    assert "relative research ranking score" in html
    assert "not statistical confidence" in html
    assert "Small score gaps should be interpreted cautiously" in html
    assert "40% price momentum" in html
    assert "25% relative strength" in html
    assert "20% volume confirmation" in html
    assert "15% breadth of participation" in html
    assert "percentile-rank normalized within the current narrative universe" in html
    assert "median narrative 7D return minus BTC 7D return" in html
    assert "median narrative 7D return minus ETH 7D return" in html
    assert "judgment-based V1 heuristics" in html
    assert "not statistically derived cutoffs" in html
    assert "80 manually curated tokens" in html
    assert "10 representative tokens per narrative" in html
    assert "not full sector coverage" in html
    assert "Taxonomy assignments involve judgment" in html


def test_concentration_review_sanitizes_broad_participation_phrase(
    tmp_path: Path,
) -> None:
    processed_dir = tmp_path / "processed" / "2026-05-25"
    processed_dir.mkdir(parents=True)
    write_ranking(processed_dir / "narrative_ranking.csv")
    pd.DataFrame(
        [
            {
                "primary_narrative": "AI",
                "top_1_market_cap_share": 0.35,
                "top_3_market_cap_share": 0.65,
                "concentration_comment": "Broad participation: market cap is more distributed",
            }
        ]
    ).to_csv(processed_dir / "sql_concentration_review.csv", index=False)

    output_path = generate_report(
        processed_root=tmp_path / "processed",
        reports_root=tmp_path / "reports",
        templates_root=Path("templates"),
    )
    html = output_path.read_text(encoding="utf-8")

    assert "Broad participation" not in html
    assert "Lower concentration: market cap is more distributed" in html
