"""Data loading helpers for Crypto Narrative Radar."""

from pathlib import Path

import pandas as pd

from crypto_narrative_radar.config import DATA_DIR


TAXONOMY_PATH = DATA_DIR / "reference" / "taxonomy.csv"


def load_taxonomy(path: Path | None = None) -> pd.DataFrame:
    """Load the crypto narrative taxonomy CSV."""
    taxonomy_path = path or TAXONOMY_PATH
    if not taxonomy_path.exists():
        raise FileNotFoundError(f"Taxonomy CSV not found: {taxonomy_path}")
    return pd.read_csv(taxonomy_path)
