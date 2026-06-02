# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the full daily pipeline (fetch → metrics → SQL analytics)
python scripts/run_daily_pipeline.py

# Individual pipeline steps
python scripts/fetch_coingecko_markets.py
python scripts/calculate_narrative_metrics.py
python scripts/run_sql_analytics.py [--date YYYY-MM-DD]

# Historical backfill (90 days)
python scripts/backfill_coingecko_history.py --days 90
python scripts/calculate_historical_narrative_metrics.py

# Streamlit dashboard
streamlit run dashboard/streamlit_app.py

# Tests
python -m pytest
python -m pytest tests/test_narrative_metrics.py   # single file
```

## Architecture

This is a **local-first, CSV-based data pipeline** with no database server, Docker, or scheduler. All state lives in files under `data/`.

### Data flow

```
data/reference/taxonomy.csv  (curated, ~80 tokens × 8 narratives)
    ↓
CoinGecko /coins/markets API
    ↓  [crypto_narrative_radar/api/coingecko.py]
data/raw/coingecko/markets/YYYY-MM-DD/
    ↓  [crypto_narrative_radar/data/market_pipeline.py]
data/processed/YYYY-MM-DD/token_market_snapshot_YYYY-MM-DD.csv
    ↓  [crypto_narrative_radar/metrics/narrative_metrics.py]
data/processed/YYYY-MM-DD/narrative_metrics.csv
data/processed/YYYY-MM-DD/narrative_ranking.csv
    ↓  [scripts/run_sql_analytics.py  +  sql/*.sql via DuckDB]
data/processed/YYYY-MM-DD/sql_*.csv
    ↓
dashboard/streamlit_app.py
```

Historical pipeline mirrors the above via `/coins/{id}/market_chart` → `data/processed/historical/`.

### Key modules

| Module | Responsibility |
|--------|---------------|
| `crypto_narrative_radar/api/coingecko.py` | `fetch_markets()`, `fetch_market_chart()` |
| `crypto_narrative_radar/data/market_pipeline.py` | Normalize + merge raw data with taxonomy |
| `crypto_narrative_radar/data/historical.py` | Process 90-day market chart responses |
| `crypto_narrative_radar/metrics/narrative_metrics.py` | `calculate_narrative_metrics()`, `add_narrative_scores()`, `create_narrative_ranking()` |
| `crypto_narrative_radar/metrics/historical_narrative_metrics.py` | Daily narrative aggregation over history |
| `crypto_narrative_radar/config.py` | Path constants (`PROJECT_ROOT`, `DATA_DIR`, etc.) — use these, never hardcode paths |

### Narrative Momentum Score (V1)

```
40%  Price Momentum      = weighted avg of 24h/7d/30d returns, percentile-ranked
25%  Relative Strength   = outperformance vs BTC and ETH 7d median, percentile-ranked
20%  Volume Confirmation = total_volume / total_market_cap, percentile-ranked
15%  Breadth             = share of tokens with positive returns, percentile-ranked

Missing components: remaining weights rebalance proportionally.
```

### Outputs per date partition

- `token_market_snapshot_YYYY-MM-DD.csv` — one row per token
- `narrative_metrics.csv` — one row per narrative (raw aggregates)
- `narrative_ranking.csv` — ranked by `narrative_momentum_score`
- `sql_narrative_summary.csv`, `sql_top_token_contributors.csv`, `sql_concentration_review.csv`

## Project Rules (from AGENTS.md)

**This is a market intelligence tool, not a trading bot.** Do not add buy/sell logic, trading signals, price predictions, or portfolio optimization. Also do not add: database, Docker, scheduler/cron, Telegram/Discord alerts, Twitter sentiment, on-chain analytics, backtesting, or complex frontend frameworks — unless explicitly approved.

**Language**: Use cautious research language ("momentum appears broad", "volume confirmation improved"). Avoid "buy", "sell", "alpha signal", "guaranteed upside", "this predicts".

**Taxonomy rules**: Each token has exactly one `primary_narrative`. Use `coingecko_id` (not just ticker symbols). No duplicate IDs. Stablecoins/wrapped assets excluded from scoring.

**Scope discipline**: Make the smallest clean change that satisfies the task. No unrelated features.

## Terminology (from CONTEXT.md)

Use these canonical terms: Narrative Momentum Score, Narrative Metrics, Narrative Ranking, Relative Strength, Volume Confirmation, Breadth of Participation, Concentration Review, Token Contributors, Market Snapshot.

## Commit style

```
feat: add X
fix: handle Y
chore: update Z
test: add tests for W
docs: improve README section
```
