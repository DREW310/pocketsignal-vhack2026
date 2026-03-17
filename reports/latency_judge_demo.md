# Latency Report

Generated: 2026-03-17T09:01:50.701546+00:00

## Run Metadata

- Scenario: `mixed_exact`
- Response profile: `judge_demo`
- Timeout seconds: `10.0`
- Error count: `0`

## Overall Roundtrip Latency (ms)

| Metric | Value |
|---|---:|
| Count | 60 |
| Avg | 877.732 |
| p50 | 37.212 |
| p95 | 2909.391 |
| p99 | 4574.600 |

## Per Route Roundtrip Latency (ms)

| Status | Count | Avg | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| Approve | 20 | 36.868 | 27.456 | 96.976 | 99.108 |
| Block | 20 | 37.986 | 32.425 | 72.341 | 95.269 |
| Flag | 20 | 2558.343 | 2213.961 | 4574.600 | 5072.341 |

## Gate C Check

- Approve/Block p95 < 50ms: False
- Flag p95 < 1s: False
