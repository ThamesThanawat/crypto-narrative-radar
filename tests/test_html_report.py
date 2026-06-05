from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from crypto_narrative_radar.reports.html_report import (
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
)


def base_ranking_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rank": 1,
                "primary_narrative": "AI",
                "narrative_momentum_score": 88,
                "avg_return_7d": 4,
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
                score_column: 92,
                "avg_return_7d": 12,
                "avg_return_30d": 20,
                "breadth_7d": 0.8,
                "total_market_cap": 1000,
                "total_volume": 100,
                "relative_strength_7d": 8,
            },
            {
                "rank": 2,
                "primary_narrative": "DeFi",
                score_column: 51,
                "avg_return_7d": 3,
                "avg_return_30d": 6,
                "breadth_7d": 0.5,
                "total_market_cap": 800,
                "total_volume": 80,
                "relative_strength_7d": 1,
            },
            {
                "rank": 3,
                "primary_narrative": "Gaming / GameFi",
                score_column: 20,
                "avg_return_7d": -2,
                "avg_return_30d": -8,
                "breadth_7d": 0.2,
                "total_market_cap": 400,
                "total_volume": 40,
                "relative_strength_7d": -4,
            },
        ]
    )
    df.to_csv(path, index=False)


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

    assert "Top 5 by Narrative Momentum Score" in html
    assert "Lowest 5 by Narrative Momentum Score" in html
    assert "<th>Narrative</th>" in html
    assert "<th>Avg 7D Return</th>" in html
    assert "<th>Narrative Momentum Score</th>" in html
    assert "Top 5 Outperforming Narratives" not in html
    assert "Top 5 Weakening Narratives" not in html
