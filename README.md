# Crypto Narrative Radar

Crypto Narrative Radar is a Python-based market intelligence project for tracking sector-level momentum across major crypto narratives.

The project focuses on research support by analyzing narrative strength, sector rotation, relative strength, volume confirmation, and breadth of participation using market data.

## Project Goals

- Build a clear, modular crypto market intelligence workflow in Python
- Track momentum across narratives such as DeFi, Layer 1, Layer 2, RWA, AI, DePIN, Gaming, and Exchange Tokens
- Produce explainable outputs for research and decision support
- Practice clean data analysis and reporting patterns suitable for portfolio and interview discussions

## Features

- Curated narrative-to-token taxonomy for core crypto sectors
- CoinGecko market data pipeline
- Raw and processed CSV snapshot outputs
- Narrative-level metrics and ranking
- Narrative Momentum Score based on price momentum, relative strength, volume confirmation, and breadth
- DuckDB SQL analytics for narrative summaries, token contributors, and concentration review
- Daily GitHub Actions automation with processed-output artifacts
- Streamlit dashboard for interactive research exploration

## Planned Improvements

- Historical backfill V1
- Static HTML research report
- Dashboard polish and recruiter-ready screenshots
- README case study and interview explanation

## Tech Stack

- Python
- pandas
- requests
- pathlib
- Streamlit
- Plotly
- Jinja2
- CSV and HTML outputs

## Repository Structure

```text
crypto_narrative_radar/
  __init__.py
  config.py
  api/
  data/
  metrics/
  reports/
  dashboard/

data/
  raw/
  processed/

reports/
templates/
tests/
```

## Status

Active portfolio build: core data pipeline, narrative scoring, SQL analytics, daily automation, and Streamlit Dashboard V1 are implemented.

Completed:
- MVP narrative taxonomy with 80 validated tokens
- CoinGecko market data pipeline
- Token-level market snapshot generation
- Narrative metrics and ranking
- Narrative Momentum Score
- DuckDB SQL analytics layer
- Daily GitHub Actions snapshot automation
- Streamlit Dashboard V1

Next:
- Research UX / finance framing review
- Dashboard polish for recruiter demo
- Historical backfill V1
- Static HTML research report
- README and portfolio polish

## Daily Snapshot Automation

- Local command: `python scripts/run_daily_pipeline.py`
- GitHub Actions workflow: `Daily Crypto Narrative Snapshot`
- Processed outputs are uploaded as GitHub Actions artifacts and are not committed back to the repository.

## Running the Streamlit Dashboard

```bash
streamlit run dashboard/streamlit_app.py
```

Run `python scripts/run_daily_pipeline.py` first if no processed data exists. The dashboard defaults to the latest processed snapshot folder and is for market intelligence and research support, not trading signals.
