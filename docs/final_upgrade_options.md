# Final Upgrade Options

This document lists the highest-value next improvements for PocketSignal if the team advances to the Final Round.

The goal is not to rebuild the product. The goal is to strengthen the current architecture without breaking the demo or the trust-preserving triage logic.

## 1. Richer wording latency: practical upgrade path

PocketSignal now supports two local `Flag` recovery modes:

- `judge_demo`: richer local wording through Ollama
- `fast_route`: deterministic local wording for lower latency

If the team advances to Final, the best next-step improvements are:

### A. Keep the model warm between requests

PocketSignal now supports Ollama `keep_alive` and optional preload on startup.

Why this matters:
- Ollama documents that models are normally kept in memory for a limited time
- cold starts increase `Flag` latency
- keeping the model loaded improves repeated demo response time

Official sources:
- Ollama API `keep_alive`: [Generate a response](https://docs.ollama.com/api/generate)
- Ollama FAQ preload / keep-alive guidance: [FAQ](https://docs.ollama.com/faq)

Recommended Final test:
- `POCKETSIGNAL_OLLAMA_KEEP_ALIVE=10m`
- `POCKETSIGNAL_OLLAMA_PRELOAD=1`

### B. Test a smaller multilingual local model

Current demo model:
- `llama3`

Good Final-round candidates to benchmark:
- `llama3.2` or `llama3.2:1b`
- `qwen2.5:1.5b` or `qwen2.5:3b`

Why these are logical:
- Ollama documents `llama3.2` as optimized for multilingual dialogue use cases
- Ollama documents `qwen2.5` as multilingual and instruction-following friendly
- smaller models can reduce latency while keeping the privacy-first local architecture

Official sources:
- [llama3.2 on Ollama](https://ollama.com/library/llama3.2)
- [qwen2.5 on Ollama](https://ollama.com/library/qwen2.5)

### C. Keep the current dual-mode architecture

Do not remove the dual-mode design.

The strongest Final narrative is:
- richer mode for human-centered recovery quality
- faster mode for stricter production latency targets

That is more defensible than pretending one mode perfectly solves both goals.

## 2. Improve explanation quality without changing the core model

The highest-value change is not replacing LightGBM.

The highest-value change is improving how risk reasons are presented:
- unusual amount pattern
- unusual timing pattern
- shared fraud network linkage
- unusual device or browser context

This makes the product easier to understand for:
- judges
- operators
- low-confidence end users

## 3. Strengthen inclusivity with one more localized template

PocketSignal already supports:
- English
- Bahasa Melayu

If time allows, the next best localization experiment is:
- Filipino / Tagalog

But this is optional for Final.

Bahasa Melayu already gives the team a credible Malaysia-based inclusivity story.

## 4. What not to do before Final

Avoid these unless there is surplus time and stable evidence:

- replacing the model stack with a graph neural network
- rebuilding the API architecture
- adding a real Telegram or WhatsApp integration
- replacing the dashboard with a complex front-end rewrite
- chasing Kaggle-style leaderboard optimization at the cost of demo stability

These changes increase risk more than they increase judging value.

## 5. Final-round principle

PocketSignal is strongest when it is presented as:

- a calibrated fraud triage layer
- a privacy-first local recovery system
- an inclusive trust-preserving workflow

It is weaker when it is presented as:

- just another fraud model
- just another local chatbot
- just another dashboard
