"""CoinGecko API helpers."""

from __future__ import annotations

import requests


COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"


def fetch_markets(coingecko_ids: list[str], vs_currency: str = "usd") -> list[dict]:
    """Fetch token market data from CoinGecko /coins/markets."""
    if not coingecko_ids:
        raise ValueError("At least one CoinGecko ID is required.")

    params = {
        "vs_currency": vs_currency,
        "ids": ",".join(coingecko_ids),
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "7d,30d",
    }

    try:
        response = requests.get(COINGECKO_MARKETS_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(f"CoinGecko market request failed: {error}") from error

    data = response.json()
    if not data:
        raise ValueError("CoinGecko returned no market data.")
    if not isinstance(data, list):
        raise ValueError("CoinGecko market response was not a list.")

    return data
