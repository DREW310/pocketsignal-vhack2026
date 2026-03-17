# Latency Report

Generated: 2026-03-17T00:00:00+08:00

## Run Metadata

- Scenario: `mixed_exact`
- Response profile: `judge_demo`
- Timeout seconds: `10.0`
- Error count: `0`

## Overall Roundtrip Latency (ms)

| Metric | Value |
|---|---:|
| Count | 60 |
| Avg | 829.598 |
| p50 | 39.834 |
| p95 | 2324.297 |
| p99 | 4792.384 |

## Per Route Roundtrip Latency (ms)

| Status | Count | Avg | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| Approve | 20 | 29.052 | 25.538 | 41.698 | 78.861 |
| Block | 20 | 39.942 | 39.578 | 56.809 | 78.824 |
| Flag | 20 | 2419.799 | 2103.032 | 4792.384 | 5431.312 |

## Gate C Check

- Approve/Block p95 < 50ms: False
- Flag p95 < 1s: False

## Interpretation

- This is the richer local wording mode used for the strongest demo experience.
- `Approve` remains fast and `Block` stays close to fast-path expectations.
- `Flag` is intentionally slower because it includes local language generation through Ollama.
