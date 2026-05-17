from datetime import date

import pandas as pd

from crypto_narrative_radar.data.market_pipeline import (
    merge_with_taxonomy,
    normalize_market_data,
    save_processed_market_snapshot,
    save_raw_market_data,
)


def test_normalize_market_data_renames_id_to_coingecko_id() -> None:
    raw_df = pd.DataFrame(
        [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 100,
            }
        ]
    )

    normalized = normalize_market_data(raw_df)

    assert "coingecko_id" in normalized.columns
    assert "id" not in normalized.columns
    assert normalized.loc[0, "coingecko_id"] == "bitcoin"


def test_normalize_market_data_keeps_expected_market_columns() -> None:
    raw_df = pd.DataFrame([{"id": "ethereum", "symbol": "eth", "name": "Ethereum"}])

    normalized = normalize_market_data(raw_df)

    expected_columns = {
        "coingecko_id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "total_volume",
        "price_change_percentage_24h",
        "price_change_percentage_7d_in_currency",
        "price_change_percentage_30d_in_currency",
        "last_updated",
    }
    assert expected_columns <= set(normalized.columns)


def test_merge_with_taxonomy_adds_metadata_and_prefers_taxonomy_names() -> None:
    market_df = normalize_market_data(
        pd.DataFrame(
            [
                {
                    "id": "fetch-ai",
                    "symbol": "fet",
                    "name": "Fetch.ai",
                    "current_price": 1.25,
                }
            ]
        )
    )
    taxonomy_df = pd.DataFrame(
        [
            {
                "coingecko_id": "fetch-ai",
                "symbol": "FET",
                "name": "Artificial Superintelligence Alliance",
                "primary_narrative": "AI",
                "secondary_narratives": "Agents; data",
                "include_in_score": True,
                "notes": "Display name differs from API ID.",
            }
        ]
    )

    merged = merge_with_taxonomy(market_df, taxonomy_df)

    assert merged.loc[0, "primary_narrative"] == "AI"
    assert merged.loc[0, "symbol"] == "FET"
    assert merged.loc[0, "name"] == "Artificial Superintelligence Alliance"
    assert merged.loc[0, "market_symbol"] == "fet"
    assert merged.loc[0, "market_name"] == "Fetch.ai"


def test_merge_with_taxonomy_preserves_one_row_per_coingecko_id() -> None:
    market_df = normalize_market_data(
        pd.DataFrame(
            [
                {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
                {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
            ]
        )
    )
    taxonomy_df = pd.DataFrame(
        [
            {
                "coingecko_id": "bitcoin",
                "symbol": "BTC",
                "name": "Bitcoin",
                "primary_narrative": "Layer 1",
                "secondary_narratives": "Store of value",
                "include_in_score": True,
                "notes": "",
            },
            {
                "coingecko_id": "ethereum",
                "symbol": "ETH",
                "name": "Ethereum",
                "primary_narrative": "Layer 1",
                "secondary_narratives": "DeFi",
                "include_in_score": True,
                "notes": "",
            },
        ]
    )

    merged = merge_with_taxonomy(market_df, taxonomy_df)

    assert len(merged) == 2
    assert not merged["coingecko_id"].duplicated().any()


def test_output_paths_use_expected_date_directories(tmp_path) -> None:
    run_date = date(2026, 5, 17)

    raw_path = save_raw_market_data(
        [{"id": "bitcoin", "symbol": "btc"}],
        run_date,
        base_dir=tmp_path / "raw",
    )
    processed_path = save_processed_market_snapshot(
        pd.DataFrame([{"coingecko_id": "bitcoin"}]),
        run_date,
        base_dir=tmp_path / "processed",
    )

    assert raw_path == (
        tmp_path
        / "raw"
        / "coingecko"
        / "markets"
        / "2026-05-17"
        / "coingecko_markets_raw_2026-05-17.csv"
    )
    assert processed_path == (
        tmp_path
        / "processed"
        / "2026-05-17"
        / "token_market_snapshot_2026-05-17.csv"
    )
    assert raw_path.exists()
    assert processed_path.exists()
