# PocketSignal Metrics Report

Generated: 2026-03-10T14:45:40.980380Z

## Core Metrics

| Metric | Value |
|---|---:|
| ROC-AUC | 0.900588 |
| PR-AUC | 0.500713 |
| Brier Score | 0.023793 |
| Precision@Block | 0.925550 |
| Recall@Block | 0.134596 |
| FPR@Block | 0.000386 |
| Fraud Rate in Approve Bucket | 0.001693 |

## Routing Thresholds

| Route | Threshold Rule |
|---|---|
| Approve | score < 21 |
| Flag | 21 <= score <= 99 |
| Block | score > 99 |

## Confusion Matrix (Block as Positive)

| Cell | Count |
|---|---:|
| TN | 114000 |
| FP | 44 |
| FN | 3517 |
| TP | 547 |

## Route Distribution

| Status | Count |
|---|---:|
| Approve | 24212 |
| Flag | 93305 |
| Block | 591 |
