from pathlib import Path


README_TEXT = Path("README.md").read_text(encoding="utf-8")


def test_readme_mentions_zero_friction_sample_report_preview() -> None:
    assert "To preview the project without cloning or running the pipeline" in README_TEXT
    assert (
        "https://ThamesThanawat.github.io/crypto-narrative-radar/showcase/sample_2026-05-20.html"
        in README_TEXT
    )


def test_readme_mentions_dashboard_data_and_watchlist_refresh_requirements() -> None:
    assert "The dashboard requires processed CSV outputs" in README_TEXT
    assert "python scripts/run_daily_pipeline.py" in README_TEXT
    assert "refreshes narrative watchlist indicators" in README_TEXT
    assert "Historical backfill remains a separate step" in README_TEXT
