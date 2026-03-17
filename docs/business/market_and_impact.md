# Market Potential and Social Impact

## Market Position

PocketSignal is a B2B2C fraud triage layer for digital wallets, super apps, neobanks, and payout platforms serving first-time or low-confidence digital finance users in ASEAN.

Our first commercial beachhead is the Philippines:
- Bangko Sentral ng Pilipinas reported that account ownership rose to 65% in 2022, but 34.3 million Filipino adults were still unbanked.
- This means inclusion is improving, but trust is still fragile.
- For wallet users who treat their stored balance as daily working capital, one fraudulent debit can immediately disrupt food, transport, or inventory spending.

## Primary Customer and End User

### Paying customer
- Digital wallet providers
- Super apps with wallet rails
- Gig economy payout platforms
- Payment processors serving QR and wallet merchants

### Protected end user
- Gig workers receiving daily wallet payouts
- Rural and neighborhood micro-merchants relying on QR or wallet acceptance

## Why This Problem Has Real Demand

1. Wallet onboarding is growing faster than fraud literacy.
2. Legacy fraud controls optimize for detection only, not for user trust recovery.
3. Hard declines are expensive in this segment because false positives can block legitimate earnings.
4. Support teams need a triage system, not just a raw fraud score.
5. World Bank notes that SMEs represent about 90% of businesses and more than 50% of employment globally, so protecting micro-merchant wallet trust has wider economic value than a narrow fraud KPI.

## What Makes PocketSignal Commercially Relevant

PocketSignal does not stop at "fraud score generated."

It turns risk into three operational actions:
- `Approve`: low-risk transactions continue with minimal friction
- `Flag`: ambiguous transactions trigger a local, user-friendly confirmation message
- `Block`: high-confidence fraud is stopped immediately

This is commercially useful because it reduces both fraud loss pressure and manual-review overload.

## Evidence From the Current Prototype

From the current full-data validation run on IEEE-CIS:
- `ROC-AUC`: `0.9006`
- `PR-AUC`: `0.5007`
- `Precision@Block`: `0.9255`
- `FPR@Block`: `0.000386`
- Fraud rate in the `Approve` bucket: `0.001693`

Operational reading:
- The `Block` lane is small and high-confidence.
- The `Approve` lane is low-risk enough to support fast, low-friction routing.
- The gray-zone `Flag` lane becomes the place for wallet-friendly confirmation and recovery.

## Business Model

PocketSignal is designed as a B2B2C infrastructure product.

### Revenue model
- Pilot setup / integration fee
- Recurring platform fee based on transaction volume reviewed
- Optional on-prem or partner-VPC deployment support
- Optional localization package for country- and language-specific user messaging

### Why partners would pay
- Lower fraud losses
- Lower false-positive cost
- Lower support burden for suspicious but recoverable transactions
- Better customer trust than a silent decline-only workflow

## Target Market Story For Judges

PocketSignal is not trying to replace every enterprise fraud stack on day one.

The initial wedge is narrower and stronger:
- wallet providers serving high-volume, low-ticket transactions
- users with lower digital literacy
- segments where trust and recovery matter almost as much as raw detection

That makes the product easier to pilot, easier to justify commercially, and easier to expand across ASEAN after proof of value.

## Social Impact and SDG 8.10

PocketSignal aligns with SDG 8.10 because it protects the reliability of digital financial access.

Impact chain:
- fewer fraudulent debits
- fewer unnecessary hard declines
- more confidence in keeping money inside formal digital channels
- more stable day-to-day income use for workers and merchants

## Quantified Impact Framing

Use this wording in the pitch:

"In our current validation run, the auto-block lane achieves 92.6% precision with a 0.0386% false-positive rate, while the approve bucket stays at only 0.169% fraud rate. That means we can reserve hard blocking for very high-confidence cases and use human-readable confirmation for the gray zone."

## Source Notes

- Bangko Sentral ng Pilipinas, 2022 Financial Inclusion Survey
- World Bank, SME Finance
