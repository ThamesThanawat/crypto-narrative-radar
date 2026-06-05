# Crypto Narrative Radar Strategy Context Pack

## 1. Purpose of This File

This file gives Codex concise strategic context for future work on Crypto Narrative Radar.
It should help keep implementation choices aligned with the portfolio direction and avoid random feature expansion.

This file is safe for the public project repository. It is not a journal, not a personal note, and must not include private personal content.

## 2. Project Purpose

Crypto Narrative Radar is a market intelligence and research support tool for monitoring crypto narrative momentum, relative strength, volume confirmation, breadth of participation, concentration, and data quality.

The project should remain explainable as a recruiter-ready Python, pandas, API, SQL, dashboard, and reporting portfolio project. It must not become a trading bot, price prediction model, buy/sell recommendation engine, backtesting system, or portfolio optimizer.

## 3. Current Strengths

- Curated narrative taxonomy with CoinGecko IDs.
- CoinGecko current market snapshot pipeline.
- Token-level and narrative-level market metrics.
- Narrative Momentum Score as a transparent research ranking tool.
- CSV outputs, DuckDB SQL analytics, Streamlit dashboard, and static HTML report generation.
- Clear project positioning as market intelligence rather than trading advice.
- Growing report QA and data sanity review around stale data, missing values, percentage formatting, and suspicious returns.

## 4. Strategic Shift

The project is evolving from a general crypto market intelligence dashboard into a post-listing risk monitoring portfolio project for exchange-related roles.

The direction is to show how market, liquidity, concentration, tokenomics, and incident evidence can support post-listing review workflows. The project should still use the existing name: Crypto Narrative Radar.

Current priority is Milestone 6.1: HTML Report QA & Data Sanity Review.

## 5. Target Role Alignment

Target roles include:

- Post-listing monitoring.
- Token operations.
- Asset listing operations.
- Exchange risk.
- Market surveillance support.
- Crypto research operations.

The portfolio should demonstrate structured evidence review, cautious interpretation, operational judgment, and clear written artifacts.

## 6. Three Core Artifacts

### Incident Investigation Memo

A concise investigation memo for a token or narrative event. It should summarize the timeline, market behavior, liquidity context, concentration concerns, evidence caveats, and recommended follow-up questions.

### Post-Listing Operations Packet

A practical packet for monitoring a listed asset after launch or after a notable market event. It should cover market activity, liquidity, volume, breadth, concentration, data quality, and operational watch items.

### Tokenomics Risk Memo

A focused memo reviewing token supply, unlocks, incentives, allocation risks, liquidity constraints, and market structure concerns. It should use cautious research language and avoid investment recommendations.

## 7. Liquidity Review Framework

### On-chain Liquidity

Review on-chain liquidity as a future or optional investigation layer. Relevant questions include pool depth, pool concentration, LP behavior, large wallet activity, bridge flows, and liquidity migration.

This project does not currently claim completed on-chain integrations.

### Off-chain / CEX Liquidity

Review exchange-facing liquidity using market cap, volume, volume-to-market-cap, concentration, token contributors, abnormal return context, and stale or missing data checks.

The goal is operational risk awareness, not trading execution.

## 8. Evidence Standards

### Time-correct Evidence

Use evidence available at the time of the event or report. Clearly separate what was known then from what was learned later.

### Avoid Hindsight Bias

Do not write as though later outcomes were obvious. Use the available evidence to explain what could reasonably have been reviewed at the time.

### Use Evidence Caveats

Call out missing data, stale data, API limits, incomplete historical coverage, ambiguous labels, and taxonomy judgment. Do not hide suspicious values silently.

## 9. Tool Roles

### Crypto Narrative Radar

Primary portfolio tool for structured market indicator monitoring, narrative-level analysis, report QA, and research support workflows.

### Arkham

Future or optional investigation tool for wallet/entity review and on-chain transaction context. Do not describe Arkham as an implemented integration unless it is actually added.

### Dune / Flipside

Future or optional investigation tools for SQL-based on-chain analytics and event-specific query work. Do not describe Dune or Flipside as completed capabilities.

### Nansen

Future or optional investigation tool for wallet labels, flows, and smart money context. Treat Nansen as external research support unless a real integration is implemented.

## 10. Roadmap

### Milestone 6.1: HTML Report QA & Data Sanity Review

Current priority. Add QA notes and sanity checks for report inputs, including stale data, missing values, zero or null prices, extreme percentage changes, token mismatches, duplicates, and historical percentage formatting.

### Milestone 6.2: Post-Listing Operations & Token Risk Packet

Create the first proof-pack artifact that connects current market indicators, liquidity review, tokenomics risks, and operational follow-up questions.

### Milestone 6.3: Incident Investigation Memo

Create a concise incident investigation memo template or case study using time-correct evidence and explicit caveats.

### Milestone 6.4: On-chain Investigation Mini Case Study

Design or produce a small on-chain investigation case study. Arkham, Dune, Flipside, or Nansen may be used as future or optional evidence sources, but should not be overclaimed.

### Milestone 6.5: README Final Portfolio Polish

Update the README to explain the post-listing risk monitoring direction, proof-pack artifacts, and role alignment while keeping the market intelligence framing.

### Milestone 7.0: Resume / LinkedIn / Interview Prep

Translate the project into concise resume bullets, LinkedIn language, and interview explanations for exchange-related roles.

## 11. Immediate Next Actions

- Finish Milestone 6.1 before starting new strategic artifacts.
- Keep the HTML report QA focused on data sanity, report trust, and research caveats.
- Start proof-pack artifacts before prioritizing Narrative Watchlist Indicators.
- Keep all outputs public-safe and recruiter-safe.
- Do not add trading signals, price prediction, backtesting, buy/sell recommendations, portfolio allocation, or private personal content.
- Do not add on-chain integrations unless explicitly scoped and implemented.
