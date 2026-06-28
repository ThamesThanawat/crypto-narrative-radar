# บันทึกการตรวจสอบเชิงลึก (Due Diligence) — ONDO Finance

**Sector:** RWA / Tokenized Treasuries & Securities
**วันที่ memo:** 2026-06-29
**ข้อมูล ณ:** ~2026-06 (point-in-time; ดู verification note ท้ายเอกสาร)
**ผู้เขียน:** Thanawat Sakulrungrojwute
**พื้นฐานข้อมูล:** ใช้ public information เท่านั้น ไม่ใช่คำแนะนำการลงทุน และไม่ใช่สัญญาณซื้อขาย

> **Thesis:** Ondo เป็น RWA *business* ที่มีคุณภาพและมี product traction จริง
> แต่ ONDO *token* ยังไม่มี claim ที่ชัดเจนบน revenue ที่ business สร้างขึ้น
> value accrual เป็นแบบ indirect และขึ้นกับ governance ทั้งโมเดลยัง
> structurally short ต่อ rate environment และยังมี supply unlock ก้อนใหญ่
> ไปจนถึงปี 2029 — ตัว business น่าลงทุนกว่าตัว token
>
> **สรุปหนึ่งบรรทัด:** I like Ondo the business more than ONDO the token.

---

## 1. ONDO คืออะไรจริง ๆ — แยกชั้นให้ชัด

write-up ส่วนใหญ่รวมสามสิ่งนี้เข้าด้วยกัน ทั้งที่ต้องแยก เพราะคำถามการลงทุน
อยู่ในช่องว่างระหว่างทั้งสาม

- **ตัว products** — USDY (tokenized note ที่ค้ำด้วย short-term US Treasuries,
  ETF shares และ bank demand deposits), OUSG (tokenized Treasuries fund แบบ
  qualified-access) และ Ondo Global Markets (tokenized stocks/ETFs สำหรับ
  investor นอกสหรัฐ) — ผู้ถือถือเพื่อ yield หรือ exposure
- **ตัว issuer / sponsor** — asset-management arm ของ Ondo เป็นผู้ structure
  products, ถือ legal claim บน underlying และเก็บ fee ระดับ product
- **ตัว ONDO token** — governance token ของ Ondo DAO และ Flux Finance ตาม
  official docs **ไม่ใช่** token ที่มี fee, staking-for-yield หรือ revenue claim

yield ไหลไป product holders ส่วน fee ไหลเข้า legal entities ของ sponsor
คำถามหลักของ memo นี้คือ **ตัว ONDO token** capture อะไรจากสองทางนั้นบ้าง

---

## 2. Value Accrual — เงินไหลไปไหน *(core angle)*

ธุรกิจมี economics จริง แต่จุดอ่อนคือ link ระหว่างธุรกิจกับ token

**Business economics (จริง):** DefiLlama แสดง Ondo Yield Assets TVL ~$2.58B,
annualized fees ~$55M และ fee 30 วัน ~$5.06M ส่วน combined Ondo Finance TVL
~$3.55B เมื่อรวม Global Markets scope [S6] โดย OUSG มี management fee 0.15%
ซึ่ง **waive ถึง Jan 1, 2027** [S1]

**Token claim (อ่อน):** ONDO เป็น governance token [S1, S2] ภายใต้ design
ปัจจุบันไม่มี claim บน product fee revenue โดยตรง — ไม่มี active fee switch
ไม่มี revenue-share ไม่มี buyback ที่ผูกกับ product fee กลไก fee-switch /
buyback-and-burn ถูกหยิบขึ้นมาเป็นเพียง temperature-check proposal ใน Flux
governance forum เท่านั้น ซึ่งยืนยันว่า **มีการถกแต่ยังไม่ implement** [S3]
อำนาจทางเศรษฐกิจเดียวของ token คือ *สิทธิ์ในการโหวต* เพื่อเปลี่ยน parameter
ที่ปัจจุบันไม่ได้ route revenue มาหา token

**ความกังวลชั้นสอง — governance reach:** Ondo มีสองขา คือ asset management
(ที่ fee ของ USDY/OUSG/GM เกิดขึ้น) กับ protocol/technology (Flux Finance)
governance scope ที่ระบุไว้สำหรับ ONDO map ไปฝั่ง protocol (Flux economic
parameters, contract upgrades) [S2, S11] ยังไม่มีหลักฐานว่า DAO governance
จะเข้าถึง revenue ของ asset-management products ได้ตามกฎหมาย ถ้าเข้าไม่ถึง
token holder อาจโหวตตัวเองเข้าไปหา revenue นั้นไม่ได้แม้อยากทำ
**จุดนี้ต้อง verify กับ legal structure และเป็น diligence gap ในตัวมันเอง**

> **So what:** ราคา ONDO ที่ขึ้นสะท้อน narrative demand และการเก็งกำไรบน
> utility ในอนาคต ไม่ใช่ claim บน business cash flow ~$55M ต่อปี และการ waive
> fee ของ OUSG ถึงปี 2027 ก็แปลว่า economics ที่รายงานตอนนี้อาจ understate
> fee ในอนาคต แต่ก็ส่งสัญญาณว่า adoption ตอนนี้ส่วนหนึ่งเป็นแบบ fee-subsidized

---

## 3. Revenue Durability — Structural Rate Sensitivity *(core angle)*

value proposition ของ product คือ spread บน Treasury yield ซึ่งผูก revenue
ไว้กับตัวแปร macro ที่ management ควบคุมไม่ได้

underlying เป็น short-duration: USDY (~$2.15B, ~3.55% 7D APY) อยู่บน short
Treasuries / short-Treasury ETF / bank deposits ส่วน OUSG (~$576M, ~3.35%
7D APY) ถือ fund จาก BlackRock, Franklin Templeton, WisdomTree และ Fidelity
โดย yield สะท้อนผ่าน NAV [S1, S7] Fed target range อยู่ที่ 3.50–3.75% หลัง
คงดอกเบี้ยในการประชุม FOMC วันที่ 17 มิ.ย. 2026

| Rate scenario | ผลต่อ product | Token read-through |
|---|---|---|
| −50 bps | Yield reprice ลงราว 50 bps เมื่อ portfolio short-duration หมุน (ไม่ทันที ตาม duration ของ underlying) | product attractiveness ลดลงเล็กน้อย |
| −100 bps | Net APY มีโอกาสลง ~100 bps ก่อน/หลัง fee | TVL growth อาจช้าลงถ้า stablecoin/DeFi yield แข่งได้ |
| −200 bps | yield advantage ของ tokenized T-bill หดชัด | narrative ต้องพึ่ง distribution / Global Markets / tokenized equities ไม่ใช่ Treasury yield |

> **Asymmetry ที่สำคัญ:** เพราะ token ไม่มี fee claim มันจึงรับ *downside*
> ของ rate ที่ลง (product demand อ่อน narrative อ่อน) แต่ไม่เคยได้ *upside*
> (fee revenue ที่สูงตอนดอกสูง) rate sensitivity เข้าถึง token ผ่าน TVL/demand
> ไม่ใช่ผ่าน cash flow ต่อ token และเมื่อ fee waiver ของ OUSG หมดในปี 2027
> ถ้า rate ลงพร้อมกัน net yield จะถูกบีบจากสองทาง

---

## 4. On-Chain — Holder Concentration *(hypothesis-driven)*

**Hypothesis:** ถ้า token ไม่ accrue value แล้วใครถือ — conviction ที่กระจาย
หรือ supply ที่กระจุกในมือ insider/strategic

Etherscan แสดง total supply ~10B กระจายใน ~200k addresses โดย circulating
supply ~4.869B [S4] concentration ระดับ address สูง: [S4, S10]

| Cohort | % ของ total supply |
|---|---|
| Top 10 holders | ~70.3% |
| Top 20 holders | ~76.5% |
| Top 100 holders | ~91.2% |

แต่ concentration ดิบ ๆ misleading ถ้าไม่ classify wallet ก่อน:

| Bucket | ~% supply | อ่านได้ว่า |
|---|---|---|
| Ondo Finance Multisig 2 (rank 1) | 54.8% | project-controlled treasury / allocation — ไม่ใช่ market float |
| CEX custody (Bithumb, Binance) | ~3.8% | retail ที่ถือผ่าน exchange custody |
| Unknown rank 2 (wallet เดียว) | 7.0% | wallet ที่ต้อง classify เป็นอันดับแรก |
| Unknown ranks 2–20 ไม่รวม CEX | ~17.9% | **diligence target ตัวจริง** |

> **อ่านได้ว่า:** ตัวเลข "76% concentrated" ส่วนใหญ่คือ project-controlled
> multisig ไม่ใช่ market whale คำถามที่สำคัญกว่าคือ supply ~18% ที่ถือโดย
> **unlabeled large wallets** นอก treasury และ exchange — น่าจะเป็น investor,
> custodian หรือ vesting-related แต่ยังไม่ยืนยัน ตราบใดที่ยังไม่ classify
> นี่คือ insider/overhang risk ที่ยังเปิดอยู่

**Supply overhang:** allocation จาก Foundation — Ecosystem Growth 52.1%,
Protocol Development 33.0%, Private Sales 12.9%, Community Access Sale 2.0% [S8]
ปัจจุบัน unlock แล้วเพียง ~48.7% เหลือ locked ~51.3% ไปจนถึง 18 ม.ค. 2029
unlock ก้อนใหญ่ถัดไป (18 ม.ค. 2027) ~1.71B ONDO (~17.1% ของ supply) แบ่งเป็น
Community 46.3% / Foundation 38.6% / Investors 15.1% — เป็น forward-dilution
ที่มีนัยสำคัญ [S9, S12]

**Data gap (เขียนตรง ๆ):** ข้อมูลที่หาได้ง่ายมีแค่ *cumulative* holder count
ซึ่งมีแต่ขึ้น บอกไม่ได้ว่า *active* conviction กระจายหรือบางลง active/
non-exchange holder trend จึงยังเป็น data gap (หมายเหตุ: ตัวเลข ~133k บน Dune
board ของทีม Ondo นับ holder ของ tokenized-equity *product* บน Global Markets
ไม่ใช่ ONDO token holder — สองตัวนี้ห้ามปนกัน) [S5]

---

## 5. Reserve & Legal Structure

การ verify เป็น **attestation-grade แบบ real-time แต่ audit-grade เฉพาะรายปี** —
ความต่างนี้สำคัญ และ documentation ก็ระวังคำตรงจุดนี้

- **OUSG:** เป็น LP interest ใน Ondo I LP ซึ่งเป็น 3(c)(7) private fund ขายภายใต้
  Rule 506(c) จำกัดเฉพาะ Qualified Purchasers / Accredited Investors ที่ผ่าน
  KYC/AML โดย NAV Consulting มี read-only access สำหรับ daily fund accounting
  ส่วน Ondo คำนวณ NAV เองและ reconcile ส่วนต่าง มี annual audit ส่งให้ investor [S1]
- **USDY:** **ไม่ได้** registered ภายใต้ Securities Act ผู้ถือได้ economic
  exposure ต่อ short-term Treasuries แต่ **ไม่มีสิทธิ์ถือหรือรับ** Treasuries
  โดยตรง ควรอธิบายว่าเป็น tokenized note ไม่ใช่ "ถือ T-bill โดยตรง" [S1]
- **Global Markets:** tokenized stocks/ETFs ที่ fully backed บวก cash-in-transit,
  overcollateralized โดย Ankura Trust ทำ daily attestation/verification,
  monthly reconciliation และ annual audits [S1]

> **So what:** ความแข็งของ structure แปรผกผันกับ accessibility — product ที่
> เข้าถึงและ trade ง่ายที่สุด (USDY) มี legal protection เบาที่สุด (unregistered
> note, economic exposure เท่านั้น) สำหรับ listing review token ที่มีโอกาส
> liquid สุดกลับค้ำด้วย structure ที่เบาสุด และ assurance แบบ real-time
> พึ่ง attestation ไม่ใช่ audit ในช่วงระหว่างรอบ audit รายปี

---

## 6. Competitive Position

Ondo ไม่ใช่ tokenized-treasury product เดี่ยว ๆ อีกต่อไป แต่กำลังกลายเป็น
RWA distribution platform ที่กว้างขึ้น (treasuries, yield assets, tokenized
securities) RWA.xyz แสดง total tokenized US Treasuries distributed value
~$14.79B โดย Ondo อยู่ที่ ~$2.8B (~18.65% platform share) [S7]

| Product / Platform | ~Value | ~7D APY |
|---|---|---|
| Ondo USDY | $2.15B | 3.55% |
| BlackRock BUIDL | $2.46B | 3.40% |
| Franklin iBENJI / BENJI | $1.59B / $0.84B | 3.49% |
| Ondo OUSG | $0.58B | 3.35% |

*(Value และ APY อ้างอิง RWA.xyz / DefiLlama, point-in-time [S6, S7])*

> **สัญญาณในคอลัมน์ APY:** yield เกาะกลุ่มแคบที่ 3.35–3.55% เพราะทุก issuer
> นั่งอยู่บน Treasury rate เดียวกัน **yield ไม่ใช่ differentiator** การแข่งขัน
> อยู่ที่ distribution, brand, access และ composability และเพราะทุกเจ้า reprice
> พร้อมกันเมื่อ rate ลง การแข่งจึงยิ่งหนีไปทาง brand/distribution ที่ Ondo
> อ่อนกว่า BlackRock และ Franklin — จุดแข็งของ Ondo คือ crypto-native
> distribution, multi-chain reach และความเร็วในการ expand product
> ส่วนจุดอ่อนคือ credibility แบบ traditional asset manager

---

## 7. Risk Summary

| Factor | View | หมายเหตุ |
|---|---|---|
| Business quality | Positive | RWA platform จริงที่มี product traction (~$3.55B combined TVL) |
| Token value accrual | Negative | ไม่มี direct fee/revenue claim ภายใต้ design ปัจจุบัน |
| Governance reach | Negative | ไม่ชัดว่า DAO เข้าถึง asset-management revenue ได้ตามกฎหมาย |
| Supply | Negative | locked ~51.3% ถึงปี 2029; unlock ~17.1% ใน ม.ค. 2027 |
| Holder concentration | Negative | อันดับ 1 เป็น project multisig; ~18% อยู่ใน unlabeled large wallets |
| Market / liquidity | Neutral–Positive | volume และ liquidity พอใช้ ไม่ใช่ dead asset |
| Reserve / legal | Watch | real-time เป็น attestation-grade; ความแข็งของ structure ต่างกันตาม product |
| Competitive | Neutral | distribution แข็ง แต่ brand อ่อนกว่า BlackRock / Franklin |

---

## 8. Recommendation

**WATCH / Defer List**

ตัว business เป็น RWA platform ที่มีคุณภาพจริง — ไม่ใช่เคส Pass (ไม่มี TVL ปลอม,
ไม่ใช่ไม่มี demand, liquidity ไม่ได้แดง) แต่ภายใต้ diligence แบบเข้ม
**business-to-token link อ่อนเกินกว่าจะ List ได้**: ONDO ไม่มี claim ที่ชัด
บน economics ของ USDY, OUSG หรือ Global Markets, governance อาจเข้าไม่ถึง
revenue นั้น และยังมี supply overhang ก้อนใหญ่ถึงปี 2029 บวกกับ concentration
ระดับ address ที่สูง risk/reward จึงยังไม่สนับสนุนการ List ในตอนนี้

**Upgrade เป็น List ถ้า:**
1. มี binding on-chain proposal หรือ legal framework ที่ทำให้ ONDO capture
   protocol/product revenue ได้จริง
2. fee switch ขยับจาก idea ใน forum ไปสู่ implementation path ที่ชัด
3. ชัดเจนว่า revenue ที่ route ได้เป็น Flux-only หรือรวม USDY/OUSG/Global Markets
   ได้ตามกฎหมาย
4. unlock เดือน ม.ค. 2027 ถูก absorb โดยไม่มี sell pressure หนัก
5. top unknown wallets ถูก classify แล้วไม่ใช่ insider/investor overhang
6. holder quality ดีขึ้น (active / non-exchange holders เพิ่ม ไม่ใช่แค่ cumulative)

**Downgrade เป็น Pass ถ้า:**
- governance scope ถูกยืนยันว่าจำกัดแค่ Flux และไม่มีทางแตะ asset-management revenue
- fee switch ถูก reject หรือเงียบยาว
- unlock ก้อนใหญ่ dump เข้า circulating supply
- unknown whale wallets เริ่มโอนเข้า exchange
- product TVL โต แต่ ONDO token ไม่ได้ benefit อะไร

---

## Sources

source จัดชั้นตามความน่าเชื่อถือ **Primary** = official Ondo / protocol docs,
governance และ on-chain explorer (อ้างอิงหลัก) **Secondary** = aggregator
ภายนอก ใช้ cross-check และ market context (methodology ต่างกันตาม provider
ตัวเลขจึงอาจไม่ตรงกัน)

**Primary**
- [S1] Ondo Finance Docs — products, fees, yield, legal & attestation — https://docs.ondo.finance/
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

*ตรงไหนที่ primary และ secondary overlap (เช่น unlock figures ปรากฏทั้งใน Ondo
Foundation blog และ Tokenomics.com) ให้ถือ primary เป็นหลักและใช้ secondary
เป็นตัวยืนยัน*

---

### Verification Note
ตัวเลขทั้งหมดเป็น point-in-time ดึงจาก public sources (Ondo official docs,
DefiLlama, RWA.xyz, Etherscan, CoinLore, Tokenomics.com) และควร re-check กับ
ข้อมูลปัจจุบันก่อนตัดสินใจ token economics, fee structure, unlock schedule และ
reserve arrangement เปลี่ยนแปลงได้ memo นี้ใช้ public information เท่านั้น
และไม่ได้พึ่งข้อมูล non-public หรือ employer-confidential ใด ๆ
