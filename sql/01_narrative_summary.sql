-- Summarize narrative-level market intelligence metrics and ranking.
-- Tables/views are registered by scripts/run_sql_analytics.py.

SELECT
    m.primary_narrative,
    m.token_count,
    m.avg_return_24h,
    m.median_return_24h,
    m.avg_return_7d,
    m.median_return_7d,
    m.avg_return_30d,
    m.median_return_30d,
    m.total_volume,
    m.total_market_cap,
    CASE
        WHEN m.total_market_cap = 0 THEN NULL
        ELSE m.total_volume / m.total_market_cap
    END AS volume_to_market_cap,
    SUM(
        CASE
            WHEN t.price_change_percentage_24h > 0 THEN 1
            ELSE 0
        END
    ) AS positive_24h_count,
    AVG(
        CASE
            WHEN t.price_change_percentage_24h > 0 THEN 1.0
            ELSE 0.0
        END
    ) AS positive_24h_share,
    r.narrative_momentum_score,
    r.rank
FROM narrative_metrics AS m
LEFT JOIN narrative_ranking AS r
    ON m.primary_narrative = r.primary_narrative
LEFT JOIN token_market_snapshot AS t
    ON m.primary_narrative = t.primary_narrative
GROUP BY
    m.primary_narrative,
    m.token_count,
    m.avg_return_24h,
    m.median_return_24h,
    m.avg_return_7d,
    m.median_return_7d,
    m.avg_return_30d,
    m.median_return_30d,
    m.total_volume,
    m.total_market_cap,
    r.narrative_momentum_score,
    r.rank
ORDER BY r.rank;
