# Preliminary PPT Slide Contents

Use this as the exact content plan for your slide deck. Keep the deck to `10` slides so the team can deliver it cleanly inside `8-9` minutes.

## Slide 1 - Title

### On-slide title
`PocketSignal`

### Subtitle
`A privacy-first fraud triage layer for unbanked digital wallet users`

### On-slide bullets
- V-HACK 2026
- Case Study 2: Digital Trust - Real-Time Fraud Shield for the Unbanked
- Team: Cache Me

### Visual
- Clean title slide
- Small product tagline
- Optional screenshot of the dashboard in the background

### Speaker
- Speaker 1

## Slide 2 - Problem

### On-slide title
`Why this problem matters`

### On-slide bullets
- Wallet balance is working capital, not spare cash
- Fraudulent debits destroy trust
- False positives also hurt real earnings
- Existing tools detect risk, but do not recover user trust

### Visual
- Simple 3-step pain flow:
  - fraud or false block
  - user panic / lost access
  - reduced trust in digital finance

### Speaker
- Speaker 1

## Slide 3 - Target User and Market

### On-slide title
`Who we protect`

### On-slide bullets
- Gig workers receiving wallet payouts
- Rural and neighborhood micro-merchants using QR or wallet rails
- Beachhead customer: wallet providers and super apps
- Philippines-first entry story due to large remaining unbanked population

### Speaker note
- Mention BSP: 65% account ownership in 2022, but 34.3 million adults still unbanked

### Visual
- Two persona cards:
  - gig worker
  - micro-merchant

### Speaker
- Speaker 1

## Slide 4 - Solution Overview

### On-slide title
`PocketSignal in one screen`

### On-slide bullets
- Score the transaction
- Route to `Approve`, `Flag`, or `Block`
- Only `Flag` triggers local explanation
- Switchable rich / fast local wording
- No external paid LLM API

### Visual
- Simple three-lane diagram:
  - Approve -> fast path
  - Flag -> local chat-style message
  - Block -> immediate stop

### Speaker
- Speaker 2

## Slide 5 - Technical Architecture

### On-slide title
`How the system works`

### On-slide bullets
- IEEE-CIS transaction + identity merge
- Behavior features: time, frequency, average amount
- Graph features: `card1-DeviceInfo`, `card1-P_emaildomain`
- LightGBM + CatBoost ensemble
- FastAPI + Streamlit + local Ollama

### Visual
- Architecture diagram with these boxes:
  - Data
  - Feature engineering
  - Model bundle
  - FastAPI
  - Ollama
  - Dashboard

### Speaker
- Speaker 2

## Slide 6 - Validation Evidence

### On-slide title
`What the model achieved`

### On-slide bullets
- `ROC-AUC: 0.9006`
- `PR-AUC: 0.5007`
- `Precision@Block: 92.6%`
- `FPR@Block: 0.0386%`
- `Approve bucket fraud rate: 0.169%`

### On-slide footer
`Thresholds are calibrated on validation data, not fixed heuristics.`

### Visual
- One compact metrics table
- Optional small ablation table excerpt

### Speaker
- Speaker 3

## Slide 7 - Live Demo

### On-slide title
`Live demo: detect, route, communicate`

### On-slide bullets
- Exact `Approve` case
- Exact `Flag` case with richer local chat-style confirmation
- Exact `Block` case
- English / Bahasa Melayu support

### Visual
- Full screenshot of the current dashboard
- Highlight:
  - left decision stream
  - right chat box

### Demo flow
1. Show `/health`
2. Send `Approve`
3. Send `Flag`
4. Send `Block`

### Speaker
- Speaker 3

## Slide 8 - Business Model

### On-slide title
`How this becomes a product`

### On-slide bullets
- B2B2C infrastructure model
- Pilot integration fee
- Recurring fee by monitored transaction volume
- Optional on-prem deployment and localization support

### Visual
- Simple revenue stack:
  - setup
  - recurring monitoring
  - enterprise support

### Speaker
- Speaker 4

## Slide 9 - Competitor Comparison

### On-slide title
`Why PocketSignal is different`

### On-slide bullets
- Rules-only systems are fast but brittle
- Generic fraud APIs score risk but do not recover trust
- PocketSignal combines graph-aware scoring, calibrated triage, and local user messaging

### Visual
- Reuse the table from `docs/business/competitive_advantage.md`

### Speaker
- Speaker 4

## Slide 10 - Roadmap and Closing

### On-slide title
`Why this can grow beyond the hackathon`

### On-slide bullets
- 3 months: pilot-ready wallet deployment
- 6 months: segment-specific policies and localization
- 12 months: multi-tenant ASEAN expansion
- Privacy-first and low-cost by design
- Bahasa Melayu pack for Malaysia-based pilots

### Closing line
`PocketSignal does not just detect fraud. It protects digital trust.`

### Speaker
- Speaker 4

## Build Rules

- Use the exact dashboard screenshots from the working prototype.
- Keep text minimal on slides; the detailed wording should come from `docs/pitch/video_script.md`.
- Do not show fixed `70 / 90` thresholds anywhere.
- If you include latency on slides, only use numbers from a valid local run of `scripts/load_test.py`.
- If you discuss latency, explain that PocketSignal supports both richer local wording and faster local wording for the `Flag` route.
