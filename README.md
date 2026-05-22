# Crypto Narrative Radar

## Project Overview

Crypto Narrative Radar is a Python-based crypto market intelligence project for tracking sector-level narrative momentum using CoinGecko market data and a custom token taxonomy.

The project compares major crypto narratives such as DeFi, Layer 1, Layer 2, RWA, AI, DePIN, Gaming / GameFi, and Exchange Tokens. It turns token-level market data into narrative-level research views for sector rotation, benchmark-relative strength, volume confirmation, breadth of participation, token contributors, and concentration review.

This is a research support project, not a trading system, price-forecasting tool, or investment advice product.

## Why This Project Exists

Crypto markets often rotate by narrative rather than by isolated token movement. A single token can move sharply, but analysts usually need to understand whether the broader narrative is also strengthening, whether participation is broad, and whether the move is supported by market activity.

Crypto Narrative Radar creates a repeatable workflow for comparing narrative momentum across sectors. It is designed to support crypto research, digital asset analysis, exchange and token monitoring, VC market mapping, and portfolio research workflows.

The core research problem:

- Which narratives are leading current market activity?
- Is leadership broad across many tokens or concentrated in a few large constituents?
- Are narratives outperforming BTC and ETH benchmarks?
- Is price movement supported by volume confirmation?
- Which tokens are driving each narrative view?

## What the Project Does

- Maintains a curated token-to-narrative taxonomy.
- Fetches token market data from CoinGecko.
- Produces daily token-level market snapshots.
- Aggregates token data into narrative-level metrics.
- Calculates a transparent Narrative Momentum Score.
- Uses DuckDB SQL for narrative summaries, token contributor analysis, and concentration review.
- Runs a daily snapshot pipeline locally or through GitHub Actions.
- Presents the outputs in a Streamlit research dashboard.

## Key Research Questions

- Which crypto narratives are showing the strongest current momentum?
- Which narratives are outperforming BTC and ETH over the selected market window?
- Is narrative momentum broad across many tokens or concentrated in a few leaders?
- Is price movement supported by volume confirmation?
- Which tokens contribute most to each narrative's market cap, volume, and return profile?
- Which narratives appear more concentrated or broadly distributed?
- What should an analyst investigate next?

## Key Features

### Narrative Taxonomy

The project uses a curated taxonomy that maps tokens to one primary narrative. This allows sector-level comparisons while avoiding double-counting in the scoring framework.

### CoinGecko Market Data Pipeline

The pipeline fetches token market data using CoinGecko IDs from the taxonomy and writes raw and processed CSV snapshots.

### Narrative Metrics and Scoring

Token-level observations are aggregated into narrative-level metrics such as returns, market cap, volume, relative strength, and breadth.

### Relative Strength vs BTC/ETH

Narrative returns are compared against BTC and ETH benchmark returns to identify sector-specific strength or weakness.

### Breadth of Participation

Breadth measures how widely participation is distributed across tokens within a narrative.

### Volume Confirmation

Volume confirmation helps evaluate whether narrative movement is supported by trading activity and liquidity.

### Token Contributor Analysis

Token contributor outputs show which assets are driving market cap, volume, and return behavior within each narrative.

### Concentration Review

Concentration review shows whether a narrative is broadly distributed or dominated by a small number of large tokens.

### DuckDB SQL Analytics Layer

DuckDB queries generate transparent analytical outputs for narrative summaries, top token contributors, and concentration review.

### Daily Snapshot Automation

GitHub Actions runs the daily pipeline and uploads processed outputs as workflow artifacts. The same pipeline can also be run locally.

### Streamlit Research Dashboard

The Streamlit dashboard provides an interactive research view for narrative leadership, sector rotation, volume confirmation, token contributors, and concentration review.

## Data Source

Crypto Narrative Radar uses CoinGecko market data for fields such as price, market cap, trading volume, and recent return windows.

The token universe is defined in:

```text
data/reference/taxonomy.csv
```

The current narrative workflow is snapshot-based. Each daily run creates a point-in-time market snapshot for the selected run date. Token-level historical backfill is available as a separate foundation for future narrative trend analysis.

## Methodology

Tokens are assigned one primary narrative so each token contributes to one scoring basket. Secondary narratives preserve research context for tokens that sit across multiple themes, but they are not double-counted in the MVP scoring framework.

The workflow is:

```text
taxonomy.csv
  -> CoinGecko market data
  -> token market snapshot
  -> narrative metrics
  -> narrative ranking
  -> SQL analytics outputs
  -> Streamlit dashboard
```

The outputs are descriptive market intelligence. They are intended to help analysts compare current narrative conditions and decide where deeper research may be useful.

## Narrative Scoring Framework

The Narrative Momentum Score is a descriptive research ranking score from 0 to 100. It compares narrative-level market conditions using a transparent weighting framework:

```text
40% price momentum
25% relative strength
20% volume confirmation
15% breadth of participation
```

Component interpretation:

- Price momentum: recent average return behavior at the narrative level.
- Relative strength: narrative performance compared with benchmark assets such as BTC and ETH.
- Volume confirmation: whether movement is supported by trading activity.
- Breadth of participation: whether participation is distributed across multiple tokens in the narrative.

The score is designed for research ranking and interpretation. It does not forecast future returns or provide investment advice.

## Dashboard / Outputs

Processed outputs are written under date-stamped folders:

```text
data/processed/YYYY-MM-DD/
```

Current processed outputs include:

- `token_market_snapshot_YYYY-MM-DD.csv`
- `narrative_metrics.csv`
- `narrative_ranking.csv`
- `sql_narrative_summary.csv`
- `sql_top_token_contributors.csv`
- `sql_concentration_review.csv`

The Streamlit dashboard includes:

- KPI cards for narrative leadership, benchmark-relative strength, participation breadth, and concentration watch.
- Narrative ranking table.
- Narrative Momentum Score bar chart.
- 7D vs 30D sector rotation view.
- Return vs volume confirmation scatter plot.
- Token contributor table.
- Concentration review.
- Methodology and interpretation guide.

## Repository Structure

```text
crypto_narrative_radar/
  api/
  data/
  dashboard/
  metrics/
  config.py

data/
  reference/
  raw/
  processed/

dashboard/
  streamlit_app.py

scripts/
  backfill_coingecko_history.py
  fetch_coingecko_markets.py
  calculate_narrative_metrics.py
  run_daily_pipeline.py
  run_sql_analytics.py
  validate_historical_market_data.py
  validate_market_snapshot.py
  validate_narrative_metrics.py
  validate_sql_outputs.py
  validate_taxonomy.py

sql/
  01_narrative_summary.sql
  02_top_token_contributors.sql
  03_concentration_review.sql

tests/

.github/
  workflows/
    daily_pipeline.yml
```

## How to Run

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the full daily pipeline:

```bash
python scripts/run_daily_pipeline.py
```

Run the Streamlit dashboard:

```bash
streamlit run dashboard/streamlit_app.py
```

Run the historical token backfill:

```bash
python scripts/backfill_coingecko_history.py --days 90
python scripts/validate_historical_market_data.py
```

This creates token-level historical market data. Narrative-level historical metrics are a separate future milestone.

Run the test suite:

```bash
python -m pytest tests
```

Optional validation commands:

```bash
python scripts/validate_taxonomy.py
python scripts/validate_market_snapshot.py
python scripts/validate_narrative_metrics.py
python scripts/validate_sql_outputs.py
```

On Windows, if Python is not available directly on `PATH`, use the virtual environment executable instead:

```powershell
.venv\Scripts\python.exe scripts\run_daily_pipeline.py
.venv\Scripts\python.exe -m pytest tests
```

## Limitations

- The current workflow is snapshot-based and does not yet provide multi-period trend analysis.
- CoinGecko data availability, field coverage, and API limits can affect pipeline runs.
- Taxonomy assignments involve judgment and should be reviewed as narratives evolve.
- The Narrative Momentum Score is descriptive and not forward-looking.
- The current methodology does not include fundamentals such as TVL, fees, revenue, stablecoin flows, developer activity, or protocol usage.
- The project is not investment advice and is not designed for trade execution.

## Future Improvements

- Historical narrative metrics for trend analysis.
- Static HTML research report.
- DeFiLlama fundamentals overlay, including TVL, fees, DEX volume, and stablecoin flows.
- More robust benchmark analysis.
- More detailed token contribution decomposition.
- Better dashboard UX, filters, and recruiter-demo screenshots.
- Optional hosted demo.
- More complete research notes per narrative.

## AI-Assisted Development Disclosure

This project was developed with AI assistance for planning, code drafting, refactoring, documentation, and debugging support.

The project owner reviewed, tested, and validated the outputs. The goal is to demonstrate practical AI-assisted development while maintaining understanding of the data pipeline, research methodology, scoring framework, and limitations.

## Recruiter / Portfolio Notes

Crypto Narrative Radar demonstrates the ability to turn raw crypto market data into explainable research outputs.

The project highlights:

- Python project structure.
- pandas data processing.
- API integration with CoinGecko.
- CSV-based data pipeline design.
- Narrative-level market analysis.
- Transparent scoring methodology.
- SQL analytics with DuckDB.
- Streamlit dashboarding for research workflows.
- GitHub Actions automation.
- Crypto market structure and narrative rotation thinking.

This project is intended to be interview-explainable for crypto research, data analyst, digital asset analyst, VC analyst, exchange-related, and market intelligence roles.
