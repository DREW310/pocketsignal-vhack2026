# Competitive Advantage Matrix

| Dimension | Internal Rules Engine | Stripe Radar | SEON | PocketSignal |
|---|---|---|---|---|
| Real-time route decision | High | High | High | High |
| Context from local behavior features | Medium | High | High | High |
| Wallet-specific recovery flow | Low | Low / Medium | Medium | High |
| Privacy-first local explanation | Low | Low | Low | High |
| Bilingual low-literacy messaging | Low | Low | Low | High |
| Works without external paid LLM API | High | High | High | High |
| Designed for Malaysia-first wallet / QR pilots | Low | Low | Low | High |

## What Actually Differentiates PocketSignal

PocketSignal is not trying to outbuild every enterprise fraud platform.

Its advantage is narrower and more specific:
- calibrated `Approve / Flag / Block` triage
- a recovery step for the gray zone instead of a silent decline
- local explanation only when needed
- simple English and Bahasa Melayu support for lower-confidence users

## Why The Comparison Is Fair

- **Internal rules engines** are fast and common, but they are brittle and usually weak on user-facing recovery.
- **Stripe Radar** is a strong cloud-native fraud product inside the Stripe ecosystem, but it is not designed around local wallet-side recovery for Malaysian QR and wallet flows.
- **SEON** is a broad fraud and AML platform with strong enrichment and rules tooling, but it is still a cloud platform rather than a narrow local-first recovery layer.
- **PocketSignal** is positioned as a lighter intervention layer: detect, route, and communicate while keeping the explanation local.

## The Four-Layer Product Logic

1. **Behavior-aware scoring**
- historical usage count
- historical average amount
- time-derived behavior patterns

2. **Context-aware graph features**
- `card1` linked to `DeviceInfo`
- `card1` linked to `P_emaildomain`
- designed to surface shared infrastructure and suspicious reuse

3. **Calibrated triage**
- `Approve`
- `Flag`
- `Block`

4. **Human-centered recovery**
- only `Flag` triggers explanation
- richer local wording and faster local wording are both available
- low-literacy mode uses genuinely simpler confirmation language
- English and Bahasa Melayu are both supported

## Why This Is Still Hard To Copy Quickly

A competitor can copy one layer.
It is harder to copy the full chain:
- calibrated risk
- operational routing
- local explanation
- user confirmation loop
- lower-literacy messaging

That system-level combination is more defensible than a single classifier or a generic chatbot wrapper.

## One-Line Judge Memory Hook

"Others only score risk. PocketSignal scores risk, chooses the intervention, and explains it in a way the user can actually act on."
