# Latency Report

Generated: 2026-03-17T11:36:36.853385+00:00

## Run Metadata

- Scenario: `mixed_exact`
- Response profile: `fast_route`
- Timeout seconds: `10.0`
- Error count: `0`

## Overall Roundtrip Latency (ms)

| Metric | Value |
|---|---:|
| Count | 60 |
| Avg | 74.579 |
| p50 | 71.411 |
| p95 | 92.267 |
| p99 | 104.399 |

## Per Route Roundtrip Latency (ms)

| Status | Count | Avg | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| Approve | 20 | 73.701 | 70.543 | 87.018 | 111.091 |
| Flag | 20 | 75.127 | 73.072 | 87.944 | 92.267 |
| Block | 20 | 74.909 | 73.278 | 99.740 | 104.399 |

## Gate C Check

- Approve/Block p95 < 50ms: False
- Flag p95 < 1s: True
