-- Identify top token contributors inside each narrative using SQL windows.
-- This is a research support view, not a trading signal.

WITH eligible_tokens AS (
    SELECT *
    FROM token_market_snapshot
    WHERE lower(CAST(include_in_score AS VARCHAR)) = 'true'
),
ranked_tokens AS (
    SELECT
        primary_narrative,
        symbol,
        name,
        coingecko_id,
        market_cap,
        total_volume,
        price_change_percentage_24h,
        price_change_percentage_7d_in_currency,
        price_change_percentage_30d_in_currency,
        CASE
            WHEN SUM(total_volume) OVER (PARTITION BY primary_narrative) = 0 THEN NULL
            ELSE total_volume / SUM(total_volume) OVER (PARTITION BY primary_narrative)
        END AS volume_share_within_narrative,
        CASE
            WHEN SUM(market_cap) OVER (PARTITION BY primary_narrative) = 0 THEN NULL
            ELSE market_cap / SUM(market_cap) OVER (PARTITION BY primary_narrative)
        END AS market_cap_share_within_narrative,
        ROW_NUMBER() OVER (
            PARTITION BY primary_narrative
            ORDER BY total_volume DESC NULLS LAST
        ) AS volume_rank_within_narrative,
        ROW_NUMBER() OVER (
            PARTITION BY primary_narrative
            ORDER BY market_cap DESC NULLS LAST
        ) AS market_cap_rank_within_narrative
    FROM eligible_tokens
)
SELECT
    primary_narrative,
    symbol,
    name,
    coingecko_id,
    market_cap,
    total_volume,
    price_change_percentage_24h,
    price_change_percentage_7d_in_currency,
    price_change_percentage_30d_in_currency,
    volume_share_within_narrative,
    market_cap_share_within_narrative,
    volume_rank_within_narrative,
    market_cap_rank_within_narrative
FROM ranked_tokens
WHERE volume_rank_within_narrative <= 5
ORDER BY primary_narrative, volume_rank_within_narrative;
