# Sustainability and Cost Model

## Sustainability Principle

PocketSignal is designed to be sustainable in three ways:
- financially sustainable for early pilots
- operationally sustainable for small fraud teams
- technically sustainable without paid closed-model lock-in

## Prototype Cost Position

For the current student prototype, the software stack is fully free:
- `LightGBM`, `CatBoost`, `SHAP`, `FastAPI`, `Streamlit`, `NetworkX`, and `Ollama` are open-source or free for local use
- There is no OpenAI API spend
- There is no per-call LLM billing
- GitHub Public and YouTube submission are free

### Prototype cash software cost per 1,000 transactions
- Model inference software: `$0`
- API/runtime software: `$0`
- Local LLM software: `$0`
- Total software licensing cost: `$0`

This does not mean real deployment has zero infrastructure cost. It means the product avoids recurring vendor inference fees and can run on partner-controlled hardware.

## Deployment Planning Assumptions

For an actual pilot, cost should be framed as infrastructure rather than model licensing:
- one lightweight scoring service for `Approve` and `Block`
- one local or partner-hosted Ollama node for `Flag` explanations
- one weekly threshold review by ops / risk staff

## Cost Logic For Judges

PocketSignal is cost-efficient because:
1. the fast tree-model path handles the decision
2. the slower LLM path is only used for gray-zone communication
3. local inference avoids external API fees and data egress fees

## Operational Sustainability

### Maintenance rhythm
- Weekly: threshold health check using FPR, route mix, and approve-bucket fraud rate
- Monthly: retrain or recalibrate with the newest labeled data
- Quarterly: review drift by country, merchant type, and device segment

### Retraining triggers
- `FPR@Block` rises materially from baseline
- Approve-bucket fraud rate doubles from baseline
- New device or email clusters appear that are not explained by existing graph features

## Failure-Mode Sustainability

PocketSignal remains usable even when part of the stack is degraded:
- If Ollama is slow or unavailable, `/predict` still returns `Approve`, `Flag`, or `Block`
- `Flag` falls back to a deterministic explanation template
- This prevents the explanation path from breaking the whole fraud API

## Why This Is Sustainable Beyond The Hackathon

- No dependence on paid proprietary APIs
- Modular training and inference stack
- Compatible with on-prem, edge, or partner-VPC deployment
- Easy to localize by changing prompts, templates, thresholds, and language packs

## Judge-Friendly Summary

Use this sentence in the pitch:

"PocketSignal is financially sustainable because the core decision engine is open-source and the explanation layer is local. We avoid both vendor lock-in and recurring API cost, while keeping the system deployable on partner-controlled infrastructure."
