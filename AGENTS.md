# AGENTS.md

## Project Overview

Crypto Narrative Radar is a Python-based market intelligence and research support tool for analyzing crypto narrative momentum using CoinGecko market data.

The project transforms token-level market data into narrative-level insights across sectors such as:

- Layer 1
- Layer 2
- DeFi
- RWA
- AI
- DePIN
- Gaming / GameFi
- Exchange Tokens

The goal is to build a recruiter-ready portfolio project that demonstrates:

- Python
- pandas
- API integration
- data cleaning
- market taxonomy
- narrative-level analysis
- scoring methodology
- CSV / HTML reporting
- Streamlit dashboard development
- crypto research thinking
- product sense

## Important Positioning

This project is a market intelligence tool, not a trading bot.

Do not describe the project as:

- a price prediction system
- a trading signal generator
- an alpha-generating model
- a buy/sell recommendation engine
- an institutional-grade trading model

Use this framing instead:

Crypto Narrative Radar helps monitor sector-level momentum, relative strength, volume confirmation, and breadth of participation across crypto narratives. It supports research, market monitoring, and investment screening workflows.

## MVP Scope

The MVP should include:

1. A machine-readable narrative taxonomy
2. CoinGecko market data fetching
3. pandas-based data cleaning
4. token-level metrics
5. narrative-level aggregation
6. relative strength versus BTC and ETH
7. volume confirmation
8. breadth of participation
9. narrative momentum scoring
10. CSV exports
11. static HTML report generation
12. Streamlit dashboard
13. recruiter-ready README documentation

Do not add the following unless explicitly approved:

- database
- Docker
- scheduler or cron automation
- Telegram / Discord alerts
- Twitter / X sentiment
- on-chain analytics
- backtesting engine
- trading signals
- buy/sell logic
- portfolio optimizer
- complex frontend framework
- major repository restructuring

## Development Workflow

For every coding task, follow this workflow:

### 1. Explore

Before editing files:

- inspect the existing repository structure
- read relevant files first
- understand current conventions
- avoid assuming missing context
- identify the smallest set of files that need changes

### 2. Plan

Before coding:

- summarize the task
- list the files to create or modify
- explain the intended approach
- keep the scope limited to the requested task
- do not add unrelated features

### 3. Code

When implementing:

- make the smallest clean change that satisfies the task
- prefer simple, modular Python
- use clear function names
- write readable pandas code
- add docstrings for public functions
- avoid unnecessary classes or abstractions
- avoid over-engineering

### 4. Verify

After coding:

- run relevant tests if available
- add focused tests when appropriate
- validate file paths
- validate CSV schemas when data files are involved
- check that generated cache files are not included

Preferred test command:

```bash
python -m pytest
```

### 5. Summarize

After completing the task, summarize:

- what changed
- which files were created or modified
- how the work was verified
- any limitations or follow-up tasks
- a suggested commit message

## Python Style

Use:

- Python 3.11+
- pandas for tabular analysis
- requests for API calls
- pathlib for file paths
- python-dotenv for environment variables if needed
- Jinja2 for HTML report generation
- Streamlit and Plotly for the dashboard

Code should be:

- clean
- modular
- beginner-to-intermediate friendly
- easy to explain in interviews
- focused on data analysis and research workflows

Avoid:

- premature optimization
- complex inheritance
- hidden magic
- unclear abstractions
- large monolithic scripts
- hardcoded absolute paths

## Repository Layout

Expected high-level structure:

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
  reference/
  raw/
  processed/

reports/
templates/
tests/
README.md
requirements.txt
pyproject.toml
AGENTS.md
```

## Data Rules

Use these folders consistently:

- `data/reference/` for manually maintained reference files
- `data/raw/` for raw API outputs
- `data/processed/` for cleaned or transformed data
- `reports/` for generated report outputs
- `templates/` for HTML templates

Do not commit:

- `__pycache__/`
- `.pyc` files
- `.env`
- virtual environments
- large raw API dumps
- local system files such as `.DS_Store`

Small sample outputs may be committed only if they help demonstrate the project.

## Narrative Taxonomy Rules

The taxonomy is representative, not exhaustive.

The main taxonomy file should be:

```text
data/reference/taxonomy.csv
```

Required columns:

```text
symbol
coingecko_id
name
primary_narrative
secondary_narratives
include_in_score
notes
```

Rules:

1. Each token should have exactly one `primary_narrative`.
2. If a token fits multiple narratives, document the overlap in `secondary_narratives`.
3. Do not duplicate the same `coingecko_id`.
4. Use CoinGecko IDs, not only ticker symbols.
5. Prefer liquid, recognizable, explainable tokens.
6. Keep the MVP token universe recruiter-friendly.
7. Stablecoins, wrapped assets, pegged assets, and tokenized funds should usually be excluded from momentum scoring.
8. Add notes for ambiguous or overlapping tokens.
9. The taxonomy should be easy to explain in an interview.

MVP narratives:

- Layer 1
- Layer 2
- DeFi
- RWA
- AI
- DePIN
- Gaming / GameFi
- Exchange Tokens

## Metrics Framework

The MVP should prioritize simple, explainable metrics.

Core metrics:

- 7D return
- 30D return
- trading volume
- market cap
- volume change
- relative strength versus BTC
- relative strength versus ETH
- breadth of participation
- narrative momentum score

Initial narrative score weighting:

```text
40% momentum
25% relative strength
20% volume confirmation
15% breadth of participation
```

The score is a research ranking tool, not a trading signal.

## Reporting Rules

Reports should communicate research insights clearly.

HTML reports should include:

- Executive Summary
- Top outperforming narratives
- Weakening narratives
- Narrative ranking table
- Token contributors
- Volume notes
- Breadth notes
- Risk notes
- Methodology

Use cautious research language.

Good language:

- "momentum appears broad"
- "volume confirmation improved"
- "relative strength increased"
- "participation narrowed"
- "the move appears concentrated"

Avoid language such as:

- "buy"
- "sell"
- "guaranteed upside"
- "this predicts"
- "alpha signal"
- "sure opportunity"

## Dashboard Rules

The Streamlit dashboard should be simple and recruiter-friendly.

Recommended sections:

- Narrative ranking table
- Narrative score chart
- 7D and 30D return comparison
- Return versus volume change chart
- Token contributor table
- Methodology explanation box

Do not turn the dashboard into a trading interface.

## Testing Expectations

When adding taxonomy functionality, tests should check:

- taxonomy file exists
- required columns exist
- `coingecko_id` has no duplicates
- `include_in_score` has valid boolean-style values

When adding data pipeline functionality, tests should check:

- expected columns exist
- empty API responses are handled
- missing values are handled safely
- output files are written to the correct folder

When adding metrics functionality, tests should check:

- calculations return expected columns
- grouping by narrative works
- relative strength is calculated correctly
- breadth is calculated correctly

## Commit Style

Use concise conventional commit messages.

Examples:

```text
chore: initialize project scaffold
docs: add agent operating instructions
feat: add MVP narrative taxonomy
test: add taxonomy validation tests
feat: add CoinGecko market data fetcher
feat: add narrative metrics pipeline
feat: generate HTML market report
feat: add Streamlit dashboard
docs: improve README methodology section
fix: handle missing CoinGecko response fields
```

## Definition of Done

A task is complete only when:

1. the requested files are created or updated
2. the implementation stays within scope
3. tests or validation checks are run when applicable
4. generated cache files are excluded
5. the result is explainable in an interview
6. the summary includes files changed and a suggested commit message

## AI-Assisted Development Note

This project may use AI-assisted coding tools for implementation speed, debugging, refactoring, and documentation support.

However, the research framework, narrative taxonomy, scoring logic, project positioning, and market interpretation should remain manually reviewed and explainable by the project owner.

The final project should demonstrate understanding, not just generated code.
