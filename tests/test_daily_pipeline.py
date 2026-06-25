import subprocess
from pathlib import Path

import pytest

from scripts.run_daily_pipeline import (
    DAILY_PIPELINE_STEPS,
    WATCHLIST_STEP_LABEL,
    refresh_watchlist_indicators_if_available,
    run_step,
)


WORKFLOW_PATH = Path(".github/workflows/daily_pipeline.yml")


def test_daily_pipeline_sequence_uses_existing_scripts() -> None:
    step_scripts = [Path(command[1]).name for _, command in DAILY_PIPELINE_STEPS]

    assert step_scripts == [
        "validate_taxonomy.py",
        "fetch_coingecko_markets.py",
        "validate_market_snapshot.py",
        "calculate_narrative_metrics.py",
        "validate_narrative_metrics.py",
        "run_sql_analytics.py",
        "validate_sql_outputs.py",
    ]


def test_run_step_raises_on_failed_subprocess(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=1, cmd=args[0])

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        run_step("Failing step", ["python", "missing.py"])


def test_daily_pipeline_skips_watchlist_generation_when_history_is_missing(
    tmp_path: Path,
    capsys,
) -> None:
    def fail_runner(*args, **kwargs):
        pytest.fail("watchlist step should not run when historical history is missing")

    refreshed = refresh_watchlist_indicators_if_available(
        history_path=tmp_path / "missing_history.csv",
        command=["python", "scripts/calculate_watchlist_indicators.py"],
        runner=fail_runner,
    )

    output = capsys.readouterr().out
    assert not refreshed
    assert (
        "Historical narrative history not found; skipping watchlist indicator generation."
        in output
    )


def test_daily_pipeline_runs_watchlist_generation_when_history_exists(
    tmp_path: Path,
    capsys,
) -> None:
    history_path = tmp_path / "narrative_market_history_90d.csv"
    history_path.write_text("date,primary_narrative\n2026-05-20,AI\n", encoding="utf-8")
    command = ["python", "scripts/calculate_watchlist_indicators.py"]
    calls: list[tuple[str, list[str]]] = []

    def fake_runner(label: str, step_command: list[str]) -> None:
        calls.append((label, step_command))

    refreshed = refresh_watchlist_indicators_if_available(
        history_path=history_path,
        command=command,
        runner=fake_runner,
    )

    output = capsys.readouterr().out
    assert refreshed
    assert calls == [(WATCHLIST_STEP_LABEL, command)]
    assert "Watchlist indicator generation completed successfully." in output


def test_daily_pipeline_workflow_exists() -> None:
    assert WORKFLOW_PATH.exists()


def test_daily_pipeline_workflow_contains_required_triggers_and_steps() -> None:
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow_text
    assert "schedule:" in workflow_text
    assert 'cron: "15 1 * * *"' in workflow_text
    assert "actions/checkout@v4" in workflow_text
    assert "actions/setup-python@v5" in workflow_text
    assert "python scripts/run_daily_pipeline.py" in workflow_text
    assert "python -m pytest tests" in workflow_text
    assert "actions/upload-artifact@v4" in workflow_text
    assert "path: data/processed/" in workflow_text
    assert "git commit" not in workflow_text
    assert "git push" not in workflow_text
