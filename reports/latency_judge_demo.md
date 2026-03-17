# Latency Report

Generated: 2026-03-17T11:35:40.837227+00:00

## Run Metadata

- Scenario: `mixed_exact`
- Response profile: `judge_demo`
- Timeout seconds: `10.0`
- Error count: `0`

## Overall Roundtrip Latency (ms)

| Metric | Value |
|---|---:|
| Count | 60 |
| Avg | 548.577 |
| p50 | 31.894 |
| p95 | 1686.319 |
| p99 | 1697.511 |

## Per Route Roundtrip Latency (ms)

| Status | Count | Avg | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| Block | 20 | 31.715 | 29.150 | 36.210 | 76.943 |
| Approve | 20 | 30.031 | 25.905 | 45.293 | 77.497 |
| Flag | 20 | 1583.984 | 1595.854 | 1697.511 | 1954.854 |

## Gate C Check

- Approve/Block p95 < 50ms: True
- Flag p95 < 1s: False
