from pathlib import Path

import pandas as pd

from crypto_narrative_radar.config import DATA_DIR


TAXONOMY_PATH = DATA_DIR / "reference" / "taxonomy.csv"
REQUIRED_COLUMNS = [
    "symbol",
    "coingecko_id",
    "name",
    "primary_narrative",
    "secondary_narratives",
    "include_in_score",
    "notes",
]
VALID_BOOLEAN_VALUES = {"TRUE", "FALSE", "True", "False", "true", "false", True, False}


def test_taxonomy_csv_exists() -> None:
    assert Path(TAXONOMY_PATH).exists()


def test_taxonomy_required_columns_exist() -> None:
    taxonomy = pd.read_csv(TAXONOMY_PATH)

    assert list(taxonomy.columns) == REQUIRED_COLUMNS


def test_taxonomy_has_no_duplicate_symbols() -> None:
    taxonomy = pd.read_csv(TAXONOMY_PATH)

    assert not taxonomy["symbol"].astype(str).str.upper().duplicated().any()


def test_taxonomy_has_no_duplicate_coingecko_ids() -> None:
    taxonomy = pd.read_csv(TAXONOMY_PATH)

    assert not taxonomy["coingecko_id"].astype(str).str.lower().duplicated().any()


def test_taxonomy_primary_narrative_is_single_value() -> None:
    taxonomy = pd.read_csv(TAXONOMY_PATH)

    assert not taxonomy["primary_narrative"].isna().any()
    assert not taxonomy["primary_narrative"].astype(str).str.contains(r"[,;|]").any()


def test_include_in_score_uses_boolean_values() -> None:
    taxonomy = pd.read_csv(TAXONOMY_PATH)
    values = set(taxonomy["include_in_score"].dropna().unique())

    assert values <= VALID_BOOLEAN_VALUES
