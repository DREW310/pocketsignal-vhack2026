# Market Potential and Social Impact

## Market Position

PocketSignal is a B2B2C fraud triage layer for digital wallets, QR-payment ecosystems, super apps, and payout platforms.

Our pilot story is Malaysia-first.

That is a logical starting point for two reasons:
- Malaysia already has a large real-time QR and wallet acceptance footprint, so trust failures can affect everyday payments at national scale.
- The product can be piloted locally by a Malaysian team, then adapted for lower-confidence or less-banked ASEAN segments.

## Why Malaysia Is A Valid Starting Point

- PayNet stated in February 2026 that there are more than **2.9 million DuitNow QR merchants across Malaysia**.
- The World Bank Global Findex 2021 microdata shows that **91.4% of Malaysian adults had an account**. That means the next problem is not only access, but trusted usage.
- Royal Malaysia Police (PDRM) scam alerts in January 2026 warned that scammers are already using **AI-generated voice deception** to pressure victims into urgent transfers.

Operational reading:
- Malaysia is not “too banked” for this problem.
- It is exactly the kind of market where digital-payment infrastructure is mature, but scam pressure and trust erosion can still damage adoption.

## Primary Customer and End User

### Paying customer
- Digital wallet providers
- Super apps with wallet or QR payment rails
- Payout platforms serving gig workers
- Payment processors and acquirers supporting wallet and QR merchants

### Protected end user
- Gig workers receiving wallet payouts
- Micro-merchants depending on QR or wallet transactions for daily cash flow
- Users with lower fraud literacy or lower confidence when responding to suspicious payment alerts

## Why This Problem Has Real Demand

1. Digital-payment usage is growing faster than fraud literacy.
2. Hard declines are expensive when the user depends on wallet balance as working capital.
3. Many fraud tools optimize only for scoring, not for trust-preserving recovery.
4. Wallet operators need a route decision, not just a raw probability.
5. In Malaysia and across ASEAN, QR and wallet flows now sit close to daily income and daily spending, so trust failures affect real economic participation.

## What Makes PocketSignal Commercially Relevant

PocketSignal converts model output into three operational actions:
- `Approve`: low-risk transactions continue with minimal friction
- `Flag`: gray-zone transactions trigger a local confirmation and recovery step
- `Block`: the highest-confidence fraud lane is stopped immediately

This matters commercially because it helps operators avoid two extremes:
- approving too much risk
- blocking too many legitimate users

## Evidence From The Current Prototype

From the current full-data validation run on IEEE-CIS:
- `ROC-AUC`: `0.9006`
- `PR-AUC`: `0.5007`
- `Precision@Block`: `77.0%`
- `FPR@Block`: `0.3569%`
- Fraud rate in the `Approve` bucket: `0.4552%`

Operational reading from the calibrated routing run:
- `Approve`: `73,817` transactions (`62.5%` of the validation split)
- `Flag`: `42,519` transactions (`36.0%`)
- `Block`: `1,772` transactions (`1.5%`)

This is materially more operational than the earlier conservative trust-only routing, which pushed too much traffic into the gray zone.
It also matters that `Flag` no longer means "send everything to human review". In the current prototype, the user can confirm or deny the payment directly in the recovery loop, so only denied or unresolved flagged cases need operator follow-up.

## Why The Route Mix Now Makes More Sense

PocketSignal is no longer presenting a prototype where almost every transaction falls into `Flag`.

With the current calibrated thresholds:
- most transactions stay on the `Approve` fast path
- only the uncertain middle enters the recovery flow
- the `Block` lane remains narrow enough to avoid a blunt-force fraud policy

That makes the product easier to defend as an operator-facing system, not just a technical demo.

## Business Model

PocketSignal is designed as a B2B2C infrastructure product.

### Revenue model
- Pilot setup and integration fee
- Recurring platform fee tied to monitored transaction volume
- Optional partner-VPC or on-prem deployment support
- Optional localization package for language, wording, and market-specific risk policy tuning

### Why partners would pay
- Lower fraud loss exposure
- Lower false-positive cost than a block-heavy policy
- Better user trust than silent decline workflows
- Fewer cases escalated into human handling than a review-everything model, because part of the gray zone can be resolved through direct user confirmation

## Target Market Story For Judges

PocketSignal is not trying to replace every enterprise fraud stack in phase one.

The first wedge is narrower:
- QR and wallet ecosystems
- low-ticket but high-frequency payment flows
- segments where trust recovery matters almost as much as raw fraud detection

That makes the product more realistic to pilot and easier to justify commercially.

## Social Impact and SDG 8.10

PocketSignal aligns with SDG 8.10 because it helps people use formal digital financial channels with more confidence.

Impact chain:
- fewer fraudulent debits
- fewer unnecessary hard stops
- clearer user confirmation when the model is uncertain
- higher trust in keeping earnings and payments inside formal digital systems

## Judge-Friendly Summary

Use this wording in the pitch:

"PocketSignal is a Malaysia-first fraud triage layer for wallet and QR ecosystems. In our current calibrated routing run, about 62.5 percent of validation traffic stays on the Approve fast path, about 36 percent enters the gray-zone recovery flow, and only 1.5 percent enters the narrow Block lane. Because the gray zone can be resolved through direct user confirmation or denial, the route mix is more operational than a review-everything system while still preserving user trust."

## Source Notes

- PayNet press release on DuitNow QR merchant scale
- World Bank Global Findex 2021 microdata for Malaysia
- Royal Malaysia Police scam alert notices
