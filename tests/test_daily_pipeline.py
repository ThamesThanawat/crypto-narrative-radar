import subprocess
from pathlib import Path

import pytest

from scripts.run_daily_pipeline import DAILY_PIPELINE_STEPS, run_step


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
