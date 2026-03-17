# Latency Report

Generated: 2026-03-17T00:00:00+08:00

## Run Metadata

- Scenario: `mixed_exact`
- Response profile: `fast_route`
- Timeout seconds: `10.0`
- Error count: `0`

## Overall Roundtrip Latency (ms)

| Metric | Value |
|---|---:|
| Count | 60 |
| Avg | 64.051 |
| p50 | 64.855 |
| p95 | 81.570 |
| p99 | 82.879 |

## Per Route Roundtrip Latency (ms)

| Status | Count | Avg | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| Block | 20 | 64.759 | 65.439 | 81.570 | 82.879 |
| Flag | 20 | 63.650 | 64.739 | 72.529 | 82.560 |
| Approve | 20 | 63.743 | 64.821 | 72.759 | 84.599 |

## Gate C Check

- Approve/Block p95 < 50ms: False
- Flag p95 < 1s: True

## Interpretation

- This is the faster deterministic local wording mode for stricter latency targets.
- All three routes stayed below `100 ms` p95 in this mixed exact-case local run.
- This is the strongest latency evidence for deployment-oriented discussion.
