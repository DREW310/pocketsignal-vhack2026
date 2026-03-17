# Sustainability and Pilot Cost Model

## Sustainability Principle

PocketSignal is designed to be sustainable in three ways:
- financially sustainable for early pilots
- operationally sustainable for small fraud teams
- technically sustainable without paid LLM lock-in

## What Is Free In The Current Prototype

For the current student prototype, the software stack is free to run locally:
- `LightGBM`, `CatBoost`, `FastAPI`, `Streamlit`, `NetworkX`, and `Ollama` are open-source or free for local use
- there is no OpenAI API spend
- there is no per-call external LLM billing

That does **not** mean real deployment costs are zero.
It means the product avoids variable third-party AI API fees and keeps the core stack partner-controllable.

## Real Pilot Cost View

For a real Malaysia pilot, cost should be framed as infrastructure plus operations, not as magic-zero software cost.

| Component | What it covers | Cost logic |
|---|---|---|
| Scoring service node | FastAPI + model bundle for `Approve / Flag / Block` decisions | CPU-first, predictable, low-cost compared with external per-call fraud scoring |
| Local wording node | Ollama host for richer local wording when enabled | Optional higher-cost path used only for `Flag`, not every transaction |
| Monitoring + logging | Health checks, latency tracking, route-mix review | Needed for threshold governance and auditability |
| Operator review cadence | Review of denied or unresolved gray-zone cases | Labour cost scales with route mix, so routing efficiency matters |

## Why The Architecture Is Economically Credible

1. The core decision engine is a fast tree-model path.
2. The slower wording path is only invoked for the gray zone.
3. The faster wording mode can remove local generation cost pressure when latency or compute budgets are tighter.
4. Keeping inference local avoids recurring external API charges and sensitive-data egress.

## Operational Sustainability

### Maintenance rhythm
- Weekly: check route mix, block false positives, and approve-bucket fraud rate
- Monthly: retrain or recalibrate using the newest labeled data
- Quarterly: review drift by merchant type, payment channel, device mix, and geography

### Retraining triggers
- `FPR@Block` rises materially above baseline
- approve-bucket fraud rate rises materially above baseline
- new device or email clusters emerge that are not explained by current graph features
- partner policy changes require a different route mix

## Failure-Mode Sustainability

PocketSignal remains usable even when part of the stack is degraded:
- If local Ollama is slow or unavailable, the API still returns `Approve`, `Flag`, or `Block`
- `Flag` can switch to the faster deterministic wording mode
- This prevents the explanation layer from taking down the core fraud-routing API

## Why This Is Sustainable Beyond The Hackathon

- No dependence on paid external LLM APIs
- Modular model and API stack
- Compatible with partner-VPC, on-prem, or edge-style deployment
- Easy to localize through thresholds, template packs, and language support

## Judge-Friendly Summary

Use this sentence in the pitch:

"PocketSignal is financially realistic because the core risk engine is lightweight, while the richer local wording path is only used for gray-zone cases. That keeps the system deployable without recurring external LLM fees, but still honest about infrastructure and operator cost."
