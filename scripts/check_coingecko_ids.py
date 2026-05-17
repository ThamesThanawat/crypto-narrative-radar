"""Check taxonomy CoinGecko IDs against the live /coins/list endpoint."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = PROJECT_ROOT / "data" / "reference" / "taxonomy.csv"
COINGECKO_COINS_LIST_URL = "https://api.coingecko.com/api/v3/coins/list"


def fetch_coin_ids() -> set[str]:
    """Fetch supported CoinGecko IDs from /coins/list."""
    response = requests.get(COINGECKO_COINS_LIST_URL, timeout=30)
    response.raise_for_status()
    coins = response.json()
    return {str(coin["id"]) for coin in coins if "id" in coin}


def main() -> int:
    """Print matched and missing taxonomy CoinGecko IDs."""
    taxonomy = pd.read_csv(TAXONOMY_PATH)

    try:
        coin_ids = fetch_coin_ids()
    except requests.RequestException as error:
        print(f"Could not fetch CoinGecko coin list: {error}")
        return 1
    except ValueError as error:
        print(f"Could not parse CoinGecko response: {error}")
        return 1

    taxonomy_ids = taxonomy["coingecko_id"].dropna().astype(str).tolist()
    missing_ids = sorted(
        coingecko_id for coingecko_id in taxonomy_ids if coingecko_id not in coin_ids
    )
    matched_count = len(taxonomy_ids) - len(missing_ids)

    print("CoinGecko ID check")
    print(f"Taxonomy IDs checked: {len(taxonomy_ids)}")
    print(f"Matched IDs: {matched_count}")
    print(f"Missing IDs: {len(missing_ids)}")

    if missing_ids:
        print("Missing CoinGecko IDs:")
        for coingecko_id in missing_ids:
            print(f"- {coingecko_id}")
        return 1

    print("Missing CoinGecko IDs: none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
