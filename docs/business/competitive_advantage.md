# Competitive Advantage Matrix

| Dimension | Rules-Only Wallet Screening | Generic Fraud API | PocketSignal |
|---|---|---|---|
| Real-time route triage | Medium | Medium | High |
| Behavior profiling from transaction history | Low | Medium | High |
| Graph-aware contextual signals | Low | Low / Medium | High |
| User-facing recovery workflow | Low | Low | High |
| Privacy-first local explanation | Low | Low | High |
| Low-literacy-friendly interface | Low | Low | High |
| Free prototype / no paid LLM dependency | Medium | Low | High |

## What Actually Differentiates PocketSignal

PocketSignal is not just "LightGBM + dashboard."

Its advantage comes from the combination of four layers:

1. **Behavior-aware scoring**
- historical transaction count
- historical average amount
- time-based pattern features

2. **Context-aware graph features**
- `card1` to `DeviceInfo`
- `card1` to `P_emaildomain`
- designed to surface shared infrastructure and suspicious clusters

3. **Calibrated triage, not a single raw score**
- `Approve`
- `Flag`
- `Block`

4. **Human-centered recovery**
- only `Flag` cases trigger explanation
- explanation is local and privacy-first
- response can switch between richer local wording and faster deterministic local wording
- message is simplified for lower digital literacy users
- message can be delivered in English or Bahasa Melayu

## Why This Is Harder To Copy Than It Looks

Competitors can copy one layer. They usually do not copy the whole system design.

PocketSignal's defensible value is the full chain:
- model score
- calibrated routing
- local explanation
- low-literacy user confirmation UX

That is more defensible than a single classifier or a generic chatbot wrapper.

## Competitor Framing For The Pitch

Use this short comparison:

- Rules-only systems are fast, but brittle and easy to evade.
- Generic fraud APIs can score risk, but often remain black-box and cloud-dependent.
- PocketSignal adds graph context, calibrated triage, and local user recovery in one loop.

## One-Line Judge Memory Hook

"Others only detect. PocketSignal detects, decides, and communicates in a way that protects trust."
