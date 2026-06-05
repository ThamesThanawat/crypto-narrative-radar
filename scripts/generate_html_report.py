"""Generate a static HTML research report from processed CSV outputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.reports.html_report import (
    prepare_report_context,
    render_report,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a static Crypto Narrative Radar HTML report."
    )
    parser.add_argument("--date", help="Processed snapshot date, for example 2026-05-25.")
    return parser.parse_args()


def main() -> int:
    """Generate the report and print output paths."""
    args = parse_args()
    try:
        context = prepare_report_context(args.date)
        output_path = render_report(context)
    except (FileNotFoundError, ValueError) as error:
        print(f"HTML report generation failed: {error}")
        return 1

    latest_path = output_path.parent / "latest.html"
    print("Static HTML research report generated")
    print(f"Report: {output_path}")
    print(f"Latest: {latest_path}")
    qa_warnings = context.get("qa_warnings", [])
    if qa_warnings:
        print("Data quality warnings:")
        for warning in qa_warnings:
            print(f"- {warning}")
    else:
        print("Data quality warnings: none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
