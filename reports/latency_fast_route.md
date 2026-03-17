# Latency Report

Generated: 2026-03-17T09:01:37.544216+00:00

## Run Metadata

- Scenario: `mixed_exact`
- Response profile: `fast_route`
- Timeout seconds: `10.0`
- Error count: `0`

## Overall Roundtrip Latency (ms)

| Metric | Value |
|---|---:|
| Count | 60 |
| Avg | 86.809 |
| p50 | 82.677 |
| p95 | 121.346 |
| p99 | 130.708 |

## Per Route Roundtrip Latency (ms)

| Status | Count | Avg | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| Flag | 20 | 85.638 | 87.349 | 110.790 | 121.696 |
| Approve | 20 | 87.648 | 87.910 | 113.324 | 116.203 |
| Block | 20 | 87.141 | 80.234 | 130.708 | 139.829 |

## Gate C Check

- Approve/Block p95 < 50ms: False
- Flag p95 < 1s: True
