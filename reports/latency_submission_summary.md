# PocketSignal Latency Submission Summary

Use this file for slides and judge prep so the two latency modes are not mixed up.

## Summary

PocketSignal now supports two valid local `Flag` recovery modes:

1. `judge_demo`
- prioritizes richer local wording through Ollama
- best for demo quality and human-centered recovery storytelling

2. `fast_route`
- prioritizes deterministic local wording
- best for stricter latency targets

## Measured Results

| Mode | Approve p95 | Flag p95 | Block p95 | Notes |
|---|---:|---:|---:|---|
| `judge_demo` | 41.698 ms | 4792.384 ms | 56.809 ms | richer local generation path |
| `fast_route` | 72.759 ms | 72.529 ms | 81.570 ms | deterministic local wording path |

## What We Can Say Accurately

- PocketSignal supports both a richer local explanation mode and a faster local wording mode.
- In the current mixed exact-case local benchmark, `fast_route` kept all three routes under `100 ms` p95.
- In the current mixed exact-case local benchmark, `judge_demo` delivered the strongest user-facing wording but a much slower `Flag` path.

## What We Should Not Say

- Do not say every route is under `50 ms`.
- Do not say the richer wording path is sub-second.
- Do not mix the two modes into one latency claim.
