from pathlib import Path

import pandas as pd
import pytest

from crypto_narrative_radar.reports.html_report import (
    detect_score_column,
    find_latest_processed_date,
    generate_report,
    load_required_csv,
    prepare_executive_summary,
    prepare_report_context,
)


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
