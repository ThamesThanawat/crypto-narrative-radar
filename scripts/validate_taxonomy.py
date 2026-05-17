"""Validate the local crypto narrative taxonomy CSV."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crypto_narrative_radar.data.loaders import load_taxonomy


REQUIRED_COLUMNS = [
    "symbol",
    "coingecko_id",
    "name",
    "primary_narrative",
    "secondary_narratives",
    "include_in_score",
    "notes",
]


def _is_blank(value: object) -> bool:
    return str(value).strip() == "" or str(value).strip().lower() == "nan"


def validate_taxonomy() -> list[str]:
    """Return a list of validation errors for the taxonomy CSV."""
    errors: list[str] = []
    taxonomy = load_taxonomy()

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in taxonomy.columns
    ]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        return errors

    if taxonomy.empty:
        errors.append("Taxonomy CSV has no token rows yet.")

    for column in ["symbol", "coingecko_id", "primary_narrative"]:
        blank_rows = taxonomy[taxonomy[column].apply(_is_blank)]
        if not blank_rows.empty:
            row_numbers = ", ".join(str(index + 2) for index in blank_rows.index)
            errors.append(f"{column} is empty on CSV row(s): {row_numbers}")

    duplicate_symbols = taxonomy[
        taxonomy["symbol"].astype(str).str.upper().duplicated(keep=False)
    ]["symbol"].tolist()
    if duplicate_symbols:
        errors.append(
            "Duplicate symbols found: "
            + ", ".join(sorted(set(str(symbol) for symbol in duplicate_symbols)))
        )

    multiple_primary = taxonomy[
        taxonomy["primary_narrative"].astype(str).str.contains(r"[,;|]", na=False)
    ]
    if not multiple_primary.empty:
        symbols = ", ".join(multiple_primary["symbol"].astype(str).tolist())
        errors.append(
            "primary_narrative should contain only one narrative per token: "
            + symbols
        )

    return errors


def main() -> int:
    """Print a human-readable taxonomy validation summary."""
    taxonomy = load_taxonomy()
    errors = validate_taxonomy()

    print("Taxonomy validation summary")
    print(f"Rows: {len(taxonomy)}")
    print(f"Unique symbols: {taxonomy['symbol'].nunique() if 'symbol' in taxonomy else 0}")

    if "primary_narrative" in taxonomy:
        narratives = sorted(
            narrative
            for narrative in taxonomy["primary_narrative"].dropna().astype(str).unique()
            if narrative.strip()
        )
    else:
        narratives = []
    print("Primary narratives:")
    if narratives:
        for narrative in narratives:
            print(f"- {narrative}")
    else:
        print("- none")

    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation errors: none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
