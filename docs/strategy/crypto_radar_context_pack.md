# Crypto Radar Context Pack for Codex

## Purpose of This File

This file gives Codex the strategic context for the Crypto Narrative Radar / Crypto Listing Radar project.

Use this file when working inside this repository so that implementation decisions stay aligned with the project goal.

This file is portfolio-safe. It should not contain private journal notes, personal finance information, or unrelated Thames OS content.

---

## Project Purpose

This project is evolving from a crypto market intelligence dashboard into a post-listing risk monitoring portfolio project.

The goal is to demonstrate practical ability relevant to a Binance Post Listing Account Manager role.

The project should not only show charts or market signals. It should produce institutional-style work products that resemble what a post-listing, token risk, or exchange operations team would actually use.

---

## Current Strengths

The project already has strength in:

* crypto market intelligence
* token/listing monitoring
* off-chain market data analysis
* CoinGecko-based market data workflow
* dashboard/report generation
* signal tracking
* structured portfolio project development

Current limitation:

The project currently leans more toward market monitoring than post-listing risk operations.

---

## Strategic Shift

Do not keep adding random dashboard features.

The next phase should focus on creating recruiter-friendly institutional artifacts.

The key shift is:

From:

* more indicators
* more watchlist sections
* more charts

To:

* incident investigation
* post-listing operations workflow
* tokenomics risk review
* data sanity and QA evidence
* portfolio-ready documentation

The project should become a credible post-listing risk monitoring portfolio, not just a crypto dashboard.

---

## Target Role Alignment

The target role is Binance Post Listing Account Manager or a similar post-listing / token operations / exchange risk role.

Important skill areas to demonstrate:

* on-chain analytics awareness
* root cause analysis
* token event handling
* tokenomics risk review
* stakeholder communication
* structured operations workflow
* market and liquidity monitoring
* data quality judgment
* SQL / Python / Dune / Flipside / Nansen familiarity where possible

---

## Three Core Artifacts

### 1. Incident Investigation Memo

Purpose:

Demonstrate the ability to investigate abnormal token behavior using both off-chain and on-chain evidence.

Should include:

* observed anomaly
* timeline
* impact
* off-chain market evidence
* on-chain evidence if available
* root cause hypothesis
* contributing factors
* corrective actions
* preventive controls
* operational recommendation

This should use blameless postmortem language, not trading language.

Avoid framing like:

* signal worked
* entry point
* profitable move

Prefer framing like:

* observed anomaly
* evidence reviewed
* possible contributing factors
* root cause hypothesis
* recommended follow-up
* control improvement

---

### 2. Post-Listing Operations Packet

Purpose:

Demonstrate understanding of post-listing operational workflows.

Should include templates or docs for:

* post-listing request intake
* token swap review
* rebrand review
* mainnet migration workflow
* stakeholder update
* escalation matrix
* legal / compliance / risk handoff points
* airdrop or token event review

This artifact should show that the project understands token operations beyond market data.

---

### 3. Tokenomics Risk Memo

Purpose:

Demonstrate the ability to review token structure and risk beyond price and volume.

Should include:

* circulating supply
* total supply
* FDV
* economically relevant supply
* locked / vested / treasury / foundation supply
* unlock schedule
* cliff vs linear unlock
* insider allocation
* governance concentration
* bridge-adjusted supply
* DEX/CEX liquidity absorbency
* holder behavior around unlocks

Important concept:

Tokenomics risk is not only about unlock dates. It is about whether the market can absorb new or controlled supply without creating operational, liquidity, or reputation risk.

---

## Liquidity Review Framework

Liquidity review should separate on-chain and off-chain liquidity.

### On-chain liquidity

Review:

* DEX pools
* DEX routes
* slippage
* bridge liquidity
* pool concentration
* liquidity migration

### Off-chain / CEX liquidity

Review:

* order book depth
* spread
* slippage
* liquidity evaporation
* market maker support
* volume quality

Even if the current project does not yet have CEX order book data, the framework should acknowledge this limitation and describe how the review would work.

---

## Evidence Standards

### Time-Correct Evidence

When performing historical investigations, avoid hindsight bias.

Do not blindly use current wallet/entity labels to explain past events.

If a wallet is currently labeled as an exchange wallet, note that the label may not have been known or accurate at the time of the incident.

Use evidence caveats where needed.

Suggested wording:

> Wallet/entity labels should be interpreted using time-appropriate context where possible. Current labels may not perfectly reflect historical knowledge at the time of the event.

---

## Tool Roles

### Crypto Narrative Radar

Role:

Off-chain market intelligence layer.

Used for:

* market data
* token ranking
* return analysis
* volume movement
* listing-related monitoring
* anomaly detection candidates

### Arkham

Role:

Entity / wallet intelligence layer.

Useful for:

* labeled wallets
* exchange inflow/outflow clues
* large transfers
* suspicious wallet paths
* entity-level investigation

### Dune or Flipside

Role:

Reproducible SQL-based on-chain evidence layer.

Useful for:

* holder concentration
* transfer patterns
* DEX liquidity
* event-level analysis
* transparent query artifacts

### Nansen

Role:

Labeled holder and smart money / flow intelligence reference.

Useful for:

* holder behavior
* entity-labeled flows
* wallet segmentation
* token movement interpretation

---

## Roadmap

### Milestone 6.1: HTML Report QA & Data Sanity Review

Purpose:

Make the current report credible before adding new artifacts.

Focus areas:

* suspicious 7D / 30D return values
* missing data
* zero or null prices
* stale market data
* duplicate tokens
* token symbol mismatches
* extreme percentage changes
* calculation assumptions

Expected deliverables:

* data sanity checklist
* QA notes
* documented assumptions
* cleaned report logic where needed

---

### Milestone 6.2: Post-Listing Operations & Token Risk Packet

Expected deliverables:

* `docs/operations/post_listing_request_workflow.md`
* `docs/templates/post_listing_request_intake_template.md`
* `docs/templates/token_event_risk_review_template.md`
* `docs/templates/tokenomics_risk_review_template.md`
* `docs/templates/stakeholder_update_template.md`
* `docs/templates/escalation_matrix.md`

---

### Milestone 6.3: Incident Investigation Memo

Expected deliverables:

* `docs/case_studies/incident_investigation_template.md`
* `docs/case_studies/example_market_anomaly_investigation.md`

---

### Milestone 6.4: On-chain Investigation Mini Case Study

Expected deliverables:

* `docs/case_studies/onchain_investigation_example.md`
* `docs/research/onchain_data_sources_for_post_listing_review.md`

Use Arkham plus Flipside or Dune if possible.

---

### Milestone 6.5: README Final Portfolio Polish

Purpose:

Make the repo understandable to recruiters and hiring managers.

Focus:

* what the project does
* why it matters
* screenshots / report examples
* proof-pack artifacts
* limitations
* next steps

---

### Milestone 7.0: Resume / LinkedIn / Interview Prep

Purpose:

Convert project work into career materials.

Focus:

* resume bullets
* LinkedIn project description
* interview stories
* portfolio walkthrough script

---

## Priority Guidance

Current priority:

Finish Milestone 6.1 before adding more strategy or features.

Do not prioritize Narrative Watchlist Indicators until after the proof-pack artifacts are started.

Reason:

Narrative Watchlist is useful for market research/data analyst positioning, but the proof-pack artifacts are more aligned with Binance post-listing operations.

---

## Immediate Next Actions

1. Inspect the current repo and locate the HTML report generation flow.
2. Identify where 7D / 30D returns are calculated.
3. Identify possible causes of suspicious return values.
4. Create a data sanity checklist.
5. Document assumptions and limitations in a QA note.
6. Propose minimal code changes before implementing them.
7. Only after Milestone 6.1 is credible, proceed to the Post-Listing Operations & Token Risk Packet.
