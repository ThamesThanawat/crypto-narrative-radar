# Project Due Diligence Memo — ONDO Finance

**Sector:** RWA / Tokenized Treasuries & Securities
**Memo date:** 2026-06-29
**Data as of:** ~2026-06 (point-in-time; see verification note)
**Author:** Thanawat Sakulrungrojwute
**Basis:** Public information only. Not investment advice. Not a trading signal.

> **Thesis:** Ondo is a high-quality RWA *business* with real product traction,
> but the ONDO *token* does not currently hold a clear claim on the revenue that
> business generates. Value accrual is indirect and governance-dependent, the
> model is structurally short the rate environment, and material supply unlocks
> run through 2029. The business is more investable than the token.
>
> **In one line:** I like Ondo the business more than ONDO the token.

---

## 1. What ONDO Actually Is — Separating the Layers

Most write-ups blur three distinct things. They must be kept separate, because
the investment question lives in the gap between them.

- **The products** — USDY (tokenized note secured by short-term US Treasuries,
  ETF shares, and bank demand deposits), OUSG (qualified-access tokenized
  Treasuries fund), and Ondo Global Markets (tokenized stocks/ETFs for non-US
  investors). Users hold these for yield or exposure.
- **The issuer / sponsor** — Ondo's asset-management arm structures the products,
  holds the legal claim on the underlying, and charges product-level fees.
- **The ONDO token** — a governance token for Ondo DAO and Flux Finance. Per
  official docs it is **not** a fee-bearing, staking-for-yield, or
  revenue-claim instrument.

The yield flows to product holders; the fees accrue to the sponsor's legal
entities. The central question of this memo is what, if anything, the **ONDO
token** captures from either.

---

## 2. Value Accrual — Where the Money Flows *(core angle)*

The business has real economics. The token's link to them is the weak point.

**Business economics (real):** DefiLlama shows Ondo Yield Assets TVL of ~$2.58B,
annualized fees of ~$55M, and ~$5.06M of fees over 30 days; combined Ondo Finance
TVL is ~$3.55B including Global Markets scope. [S6] OUSG carries a 0.15% management
fee, currently **waived through Jan 1, 2027**. [S1]

**Token claim (weak):** ONDO is a governance token. [S1, S2] Under current design
it has no direct claim on product fee revenue — no active fee switch, no
revenue-share, no buyback tied to product fees. A fee-switch / buyback-and-burn
mechanism has been raised only as a temperature-check proposal in the Flux
governance forum, which confirms it is **discussed but not implemented**. [S3]
The token's only economic lever is the *right to vote* to change parameters that
do not presently route revenue to it.

**A second-order concern — governance reach.** Ondo runs two arms: asset
management (where USDY/OUSG/GM fees are generated) and protocol/technology
(Flux Finance). The governance scope documented for ONDO maps to the protocol
side (Flux economic parameters, contract upgrades). [S2, S11] It is not established
that DAO governance can legally reach the revenue of the asset-management products.
If it cannot, token holders may not be able to vote themselves into that revenue
even if they wanted to. **This requires verification against the legal structure
and is itself a diligence gap.**

> **So what:** a rising ONDO price reflects narrative demand and speculation on
> future utility, not a claim on ~$55M of annualized business cash flow. The fee
> waiver on OUSG through 2027 also means current reported economics may understate
> future fees but signal that adoption is partly fee-subsidized today.

---

## 3. Revenue Durability — Structural Rate Sensitivity *(core angle)*

The product value proposition is a spread on Treasury yield, tying revenue to a
macro variable management cannot control.

Underlyings are short-duration: USDY (~$2.15B, ~3.55% 7D APY) sits on short
Treasuries / short-Treasury ETF / bank deposits; OUSG (~$576M, ~3.35% 7D APY)
holds funds from BlackRock, Franklin Templeton, WisdomTree, and Fidelity, with
yield reflected through NAV. [S1, S7] The Fed target range is 3.50–3.75% following
the hold at the June 17, 2026 FOMC.

| Rate scenario | Product impact | Token read-through |
|---|---|---|
| −50 bps | Yield repriced down toward ~50 bps as short-duration portfolio rolls (not instant; tracks underlying duration) | Marginally weaker product appeal |
| −100 bps | Net APY likely down ~100 bps pre/post fee | TVL growth may slow if stablecoin/DeFi yields compete |
| −200 bps | Tokenized T-bill yield advantage erodes materially | Narrative must lean on distribution / Global Markets / tokenized equities, not Treasury yield |

> **The asymmetry that matters:** because the token has no fee claim, it absorbs
> the *downside* of falling rates (weaker product demand, softer narrative) but
> never captured the *upside* (higher fee revenue when rates were high). Rate
> sensitivity reaches the token through TVL/demand, not through cash flow per
> token. When the OUSG fee waiver expires in 2027, a simultaneous rate decline
> would compress net yield from both directions.

---

## 4. On-Chain — Holder Concentration *(hypothesis-driven)*

**Hypothesis:** if the token does not accrue value, who holds it — broad
conviction, or concentrated insider/strategic supply?

Etherscan shows ~10B total supply across ~200k addresses, with circulating
supply ~4.869B. [S4] Concentration at the address level is high: [S4, S10]

| Cohort | Share of total supply |
|---|---|
| Top 10 holders | ~70.3% |
| Top 20 holders | ~76.5% |
| Top 100 holders | ~91.2% |

But raw concentration is misleading without classifying the wallets:

| Bucket | ~% supply | Read |
|---|---|---|
| Ondo Finance Multisig 2 (rank 1) | 54.8% | Project-controlled treasury / allocation — not market float |
| CEX custody (Bithumb, Binance) | ~3.8% | Retail held in exchange custody |
| Unknown rank 2 (single wallet) | 7.0% | Highest-priority wallet to classify |
| Unknown ranks 2–20 ex-CEX | ~17.9% | **The real diligence target** |

> **What it means:** the headline "76% concentrated" is largely a
> project-controlled multisig, not a market whale. The more important question
> is the ~18% of supply held by **unlabeled large wallets** outside treasury and
> exchange addresses — likely investors, custodians, or vesting-related, but
> unconfirmed. Until classified, this is an open insider/overhang risk.

**Supply overhang.** Foundation allocation: Ecosystem Growth 52.1%, Protocol
Development 33.0%, Private Sales 12.9%, Community Access Sale 2.0%. [S8] Only ~48.7%
of supply is unlocked; ~51.3% remains locked through Jan 18, 2029. The next major
unlock (Jan 18, 2027) is ~1.71B ONDO (~17.1% of supply), split Community 46.3% /
Foundation 38.6% / Investors 15.1% — a material forward-dilution event. [S9, S12]

**Data gap (stated honestly):** only *cumulative* holder counts are readily
available, which only rise and cannot show whether *active* conviction is broad
or thinning. Active/non-exchange holder trend remains an open data gap. (Note:
the ~133k figure on the Ondo team's Dune board tracks tokenized-equity *product*
holders on Global Markets, not ONDO token holders — the two must not be conflated.) [S5]

---

## 5. Reserve & Legal Structure

Verification is **attestation-grade in real time, audit-grade only annually** —
a distinction that matters and that the documentation is careful about.

- **OUSG:** LP interest in Ondo I LP, a 3(c)(7) private fund sold under Rule
  506(c), restricted to Qualified Purchasers / Accredited Investors with KYC/AML.
  NAV Consulting has read-only access for daily fund accounting; Ondo computes
  NAV independently and reconciles discrepancies; annual audit delivered to
  investors. [S1]
- **USDY:** **not** registered under the Securities Act. Holders receive economic
  exposure to short-term Treasuries but **no direct right to hold or receive** the
  Treasuries. Should be described as a tokenized note, not "direct T-bill holding." [S1]
- **Global Markets:** tokenized stocks/ETFs fully backed plus cash-in-transit,
  overcollateralized, with Ankura Trust performing daily attestation/verification,
  monthly reconciliation, and annual audits. [S1]

> **So what:** structural strength is inversely related to accessibility. The most
> accessible, tradable product (USDY) carries the lightest legal protection
> (unregistered note, economic exposure only). For a listing review, the token
> most likely to be liquid is backed by the lightest structure — and real-time
> assurance rests on attestation, not audit, between annual cycles.

---

## 6. Competitive Position

Ondo is no longer a single tokenized-treasury product; it is becoming a broader
RWA distribution platform (treasuries, yield assets, tokenized securities).
RWA.xyz shows total tokenized US Treasuries distributed value ~$14.79B, with Ondo
at ~$2.8B (~18.65% platform share). [S7]

| Product / Platform | ~Value | ~7D APY |
|---|---|---|
| Ondo USDY | $2.15B | 3.55% |
| BlackRock BUIDL | $2.46B | 3.40% |
| Franklin iBENJI / BENJI | $1.59B / $0.84B | 3.49% |
| Ondo OUSG | $0.58B | 3.35% |

*(Values and APYs per RWA.xyz / DefiLlama, point-in-time. [S6, S7])*

> **The signal in the APY column:** yields cluster tightly at 3.35–3.55% because
> every issuer sits on the same underlying Treasury rate. **Yield is not a
> differentiator.** Competition is distribution, brand, access, and composability —
> and because all issuers reprice together when rates fall, the contest shifts
> further toward brand and distribution, where Ondo is weaker than BlackRock and
> Franklin. Ondo's edge is crypto-native distribution, multi-chain reach, and
> product-expansion speed; its disadvantage is traditional asset-manager credibility.

---

## 7. Risk Summary

| Factor | View | Note |
|---|---|---|
| Business quality | Positive | Real RWA platform with product traction (~$3.55B combined TVL) |
| Token value accrual | Negative | No direct fee/revenue claim under current design |
| Governance reach | Negative | Unclear whether DAO can legally reach asset-management revenue |
| Supply | Negative | ~51.3% locked through 2029; ~17.1% unlock Jan 2027 |
| Holder concentration | Negative | Top-1 is project multisig; ~18% in unlabeled large wallets |
| Market / liquidity | Neutral–Positive | Adequate volume and liquidity; not a dead asset |
| Reserve / legal | Watch | Attestation-grade real-time; structure strength varies by product |
| Competitive | Neutral | Strong distribution; weaker brand vs. BlackRock / Franklin |

---

## 8. Recommendation

**WATCH / Defer List.**

The business is a genuine, high-quality RWA platform — this is not a Pass case
(no fake TVL, no absent demand, no red-flag liquidity). But under strict research
diligence, the **business-to-token link is too weak to justify a List**: ONDO has
no clear claim on the economics of USDY, OUSG, or Global Markets, governance may
not reach that revenue, and the position carries material 2029 supply overhang
plus high address-level concentration. The risk/reward does not support List today.

**Upgrade to List if:**
1. A binding on-chain proposal or legal framework establishes that ONDO captures
   protocol/product revenue.
2. A fee switch moves from forum idea to a concrete implementation path.
3. It is clarified whether routable revenue is Flux-only or can legally include
   USDY/OUSG/Global Markets.
4. The Jan 2027 unlock is absorbed without heavy sell pressure.
5. The top unlabeled wallets are classified and are not insider/investor overhang.
6. Holder quality improves (active / non-exchange holders rising, not just
   cumulative count).

**Downgrade to Pass if:**
- Governance scope is confirmed limited to Flux with no path to asset-management
  revenue.
- The fee switch is rejected or stays dormant long-term.
- A large unlock dumps into circulating supply.
- Unknown whale wallets begin moving to exchanges.
- Product TVL grows while ONDO token captures no benefit.

---

## Sources

Sources are tiered by reliability. **Primary** = official Ondo / protocol
documentation, governance, and on-chain explorers (authoritative). **Secondary**
= third-party aggregators, used for cross-checking and market context (methodology
varies between providers, so figures may differ).

**Primary**
- [S1] Ondo Finance Docs — products, fees, yield, legal & attestation structure — https://docs.ondo.finance/
- [S2] Ondo Foundation Docs — ONDO token & governance — https://docs.ondo.foundation
- [S3] Flux Finance Governance Forum — fee-switch / buyback-and-burn temperature check (proposal stage) — https://forum.fluxfinance.com/t/temperature-check-activating-the-ondo-fee-switch-automated-programmatic-buyback-and-burn
- [S4] Etherscan — ONDO token holders & supply (0xfaba…9be3) — https://etherscan.io/token/0xfaba6f8e4a5e8ab82f62fe7c39859fa577269be3
- [S5] Dune (official @ondo) — Ondo Global Markets product holders — https://dune.com/ondo/ondo-global-markets
- [S8] Ondo Foundation Blog — "Unlocking Ondo" allocation proposal — https://blog.ondo.foundation/unlocking-ondo-a-proposal-from-the-ondo-foundation/
- [S11] Flux Finance Docs — governance scope — https://docs.fluxfinance.com/governance
- [S13] Arkham — ONDO entity / wallet labeling — https://arkm.com/explorer/token/ondo-finance

**Secondary (cross-check / market context)**
- [S6] DefiLlama — Ondo Yield Assets TVL, fees, revenue — https://defillama.com/protocol/ondo-yield-assets
- [S7] RWA.xyz — tokenized US Treasuries market & platform shares — https://app.rwa.xyz/treasuries
- [S9] Tokenomics.com — ONDO unlock schedule & vesting — https://app.tokenomics.com/tokenomics/ondo/unlocks
- [S10] CoinLore — ONDO rich list (top addresses) — https://www.coinlore.com/coin/ondo-finance/richlist
- [S12] Tokenomist.ai — ONDO unlock / supply data — https://tokenomist.ai/ondo-finance

*Where primary and secondary sources overlap (e.g. unlock figures appear in both
the Ondo Foundation blog and Tokenomics.com), the primary source is treated as
authoritative and the secondary as confirmation.*

---
All figures are point-in-time, drawn from public sources (Ondo official docs,
DefiLlama, RWA.xyz, Etherscan, CoinLore, Tokenomics.com) and should be re-checked
against current data before any decision. Token economics, fee structure, unlock
schedule, and reserve arrangements can change. This memo uses public information
only and relies on no non-public or employer-confidential material.
