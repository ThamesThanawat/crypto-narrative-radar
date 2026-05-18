-- Review whether narrative market cap and volume are concentrated.
-- Comments describe concentration for research context only.

WITH ranked_tokens AS (
    SELECT
        primary_narrative,
        coingecko_id,
        market_cap,
        total_volume,
        ROW_NUMBER() OVER (
            PARTITION BY primary_narrative
            ORDER BY market_cap DESC NULLS LAST
        ) AS market_cap_rank,
        ROW_NUMBER() OVER (
            PARTITION BY primary_narrative
            ORDER BY total_volume DESC NULLS LAST
        ) AS volume_rank
    FROM token_market_snapshot
    WHERE lower(CAST(include_in_score AS VARCHAR)) = 'true'
),
concentration AS (
    SELECT
        primary_narrative,
        COUNT(DISTINCT coingecko_id) AS token_count,
        SUM(market_cap) AS total_market_cap,
        SUM(CASE WHEN market_cap_rank = 1 THEN market_cap ELSE 0 END)
            AS top_1_market_cap,
        SUM(CASE WHEN market_cap_rank <= 3 THEN market_cap ELSE 0 END)
            AS top_3_market_cap,
        SUM(total_volume) AS total_volume,
        SUM(CASE WHEN volume_rank = 1 THEN total_volume ELSE 0 END)
            AS top_1_volume,
        SUM(CASE WHEN volume_rank <= 3 THEN total_volume ELSE 0 END)
            AS top_3_volume
    FROM ranked_tokens
    GROUP BY primary_narrative
)
SELECT
    primary_narrative,
    token_count,
    total_market_cap,
    top_1_market_cap,
    CASE
        WHEN total_market_cap = 0 THEN NULL
        ELSE top_1_market_cap / total_market_cap
    END AS top_1_market_cap_share,
    top_3_market_cap,
    CASE
        WHEN total_market_cap = 0 THEN NULL
        ELSE top_3_market_cap / total_market_cap
    END AS top_3_market_cap_share,
    total_volume,
    top_1_volume,
    CASE
        WHEN total_volume = 0 THEN NULL
        ELSE top_1_volume / total_volume
    END AS top_1_volume_share,
    top_3_volume,
    CASE
        WHEN total_volume = 0 THEN NULL
        ELSE top_3_volume / total_volume
    END AS top_3_volume_share,
    CASE
        WHEN total_market_cap = 0 THEN 'No market cap data available'
        WHEN top_1_market_cap / total_market_cap >= 0.60
            THEN 'High concentration: one token dominates market cap'
        WHEN top_3_market_cap / total_market_cap >= 0.80
            THEN 'Moderate concentration: top three tokens dominate market cap'
        ELSE 'Broad participation: market cap is more distributed'
    END AS concentration_comment
FROM concentration
ORDER BY primary_narrative;
