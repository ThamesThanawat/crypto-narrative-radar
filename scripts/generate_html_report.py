"""Generate a static HTML research report from processed CSV outputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.reports.html_report import (
    SAMPLE_REPORT_DATE,
    prepare_report_context,
    publish_showcase_report,
    render_report,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a static Crypto Narrative Radar HTML report."
    )
    parser.add_argument("--date", help="Processed snapshot date, for example 2026-05-25.")
    parser.add_argument(
        "--sample",
        action="store_true",
        help=f"Generate the pinned sample report for {SAMPLE_REPORT_DATE}.",
    )
    parser.add_argument(
        "--publish-showcase",
        action="store_true",
        help="Copy the pinned sample report to docs/showcase for portfolio publishing.",
    )
    args = parser.parse_args()
    if args.sample and args.date:
        parser.error("--sample uses the fixed sample snapshot and cannot be combined with --date.")
    if args.publish_showcase and not args.sample:
        parser.error("--publish-showcase requires --sample.")
    return args


def main() -> int:
    """Generate the report and print output paths."""
    args = parse_args()
    try:
        context = prepare_report_context(args.date, sample_mode=args.sample)
        output_path = render_report(context)
        showcase_path = (
            publish_showcase_report(output_path) if args.publish_showcase else None
        )
    except (FileNotFoundError, ValueError) as error:
        print(f"HTML report generation failed: {error}")
        return 1

    latest_path = output_path.parent / "latest.html"
    print("Static HTML research report generated")
    print(f"Report: {output_path}")
    if context.get("update_latest", True):
        print(f"Latest: {latest_path}")
    else:
        print(f"Latest unchanged: {latest_path}")
    if showcase_path is not None:
        print(f"Showcase: {showcase_path}")
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
