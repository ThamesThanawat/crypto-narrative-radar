# Crypto Narrative Radar

Crypto Narrative Radar is a Python-based market intelligence project for tracking sector-level momentum across major crypto narratives.

The project focuses on research support by analyzing narrative strength, sector rotation, relative strength, volume confirmation, and breadth of participation using market data.

## Project Goals

- Build a clear, modular crypto market intelligence workflow in Python
- Track momentum across narratives such as DeFi, Layer 1, Layer 2, RWA, AI, DePIN, Gaming, and Exchange Tokens
- Produce explainable outputs for research and decision support
- Practice clean data analysis and reporting patterns suitable for portfolio and interview discussions

## Planned Features

- Narrative-to-token mapping for core crypto sectors
- Data collection pipeline using public market data sources
- Narrative-level metrics (returns, volume trends, participation breadth)
- Relative-strength comparisons between narratives
- Streamlit dashboard for interactive exploration
- CSV and HTML report generation for weekly or ad hoc reviews

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

Early development: repository scaffold and foundational modules are being set up.

## Milestone 4.5: SQL Analytics Layer

- Uses DuckDB as an in-memory analytical SQL engine.
- Reads processed CSV outputs from `data/processed/YYYY-MM-DD/`.
- Produces SQL-derived research outputs for narrative summaries, top token contributors, and concentration review.
- Demonstrates SQL analytics skills without adding a production database.
