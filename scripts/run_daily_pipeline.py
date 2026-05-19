"""Run the full daily Crypto Narrative Radar pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

DAILY_PIPELINE_STEPS = [
    ("Validate taxonomy", [sys.executable, str(SCRIPTS_DIR / "validate_taxonomy.py")]),
    (
        "Fetch CoinGecko market data",
        [sys.executable, str(SCRIPTS_DIR / "fetch_coingecko_markets.py")],
    ),
    (
        "Validate market snapshot",
        [sys.executable, str(SCRIPTS_DIR / "validate_market_snapshot.py")],
    ),
    (
        "Calculate narrative metrics",
        [sys.executable, str(SCRIPTS_DIR / "calculate_narrative_metrics.py")],
    ),
    (
        "Validate narrative metrics",
        [sys.executable, str(SCRIPTS_DIR / "validate_narrative_metrics.py")],
    ),
    (
        "Run DuckDB SQL analytics",
        [sys.executable, str(SCRIPTS_DIR / "run_sql_analytics.py")],
    ),
    (
        "Validate SQL outputs",
        [sys.executable, str(SCRIPTS_DIR / "validate_sql_outputs.py")],
    ),
]


def run_step(label: str, command: list[str]) -> None:
    """Run one pipeline step and stop if it fails."""
    print(f"\n=== {label} ===", flush=True)
    print(" ".join(command), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> int:
    """Run all daily pipeline steps in order."""
    try:
        for label, command in DAILY_PIPELINE_STEPS:
            run_step(label, command)
    except subprocess.CalledProcessError as error:
        print(f"\nDaily pipeline failed during: {error.cmd}")
        return error.returncode

    print("\nDaily pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
