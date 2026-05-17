"""Data loading helpers for Crypto Narrative Radar."""

from pathlib import Path

import pandas as pd

from crypto_narrative_radar.config import DATA_DIR


TAXONOMY_PATH = DATA_DIR / "reference" / "taxonomy.csv"


def load_taxonomy(path: Path = TAXONOMY_PATH) -> pd.DataFrame:
    """Load the crypto narrative taxonomy CSV."""
    return pd.read_csv(path)
