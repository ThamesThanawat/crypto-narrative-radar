"""CoinGecko API helpers."""

from __future__ import annotations

import requests


COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_MARKET_CHART_ENDPOINT = "/coins/{id}/market_chart"


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


def fetch_market_chart(
    coingecko_id: str,
    vs_currency: str = "usd",
    days: int = 90,
    interval: str = "daily",
    timeout: int = 30,
) -> dict:
    """Fetch historical market chart data from CoinGecko /coins/{id}/market_chart."""
    if not coingecko_id or not coingecko_id.strip():
        raise ValueError("A CoinGecko ID is required.")

    endpoint = COINGECKO_MARKET_CHART_ENDPOINT.format(id=coingecko_id.strip())
    url = f"{COINGECKO_BASE_URL}{endpoint}"
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": interval,
    }
    headers = {"User-Agent": "crypto-narrative-radar/0.1"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(f"CoinGecko market chart request failed: {error}") from error

    data = response.json()
    if not data:
        raise ValueError("CoinGecko returned no market chart data.")
    if not isinstance(data, dict):
        raise ValueError("CoinGecko market chart response was not a dictionary.")

    return data
