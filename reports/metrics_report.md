# PocketSignal Metrics Report

Generated: 2026-03-17T08:47:24.835066Z

## Core Metrics

| Metric | Value |
|---|---:|
| ROC-AUC | 0.900588 |
| PR-AUC | 0.500713 |
| Brier Score | 0.023793 |
| Precision@Block | 0.770316 |
| Recall@Block | 0.335876 |
| FPR@Block | 0.003569 |
| Fraud Rate in Approve Bucket | 0.004552 |

## Routing Thresholds

| Route | Threshold Rule |
|---|---|
| Approve | score < 63 |
| Flag | 63 <= score <= 98 |
| Block | score > 98 |

## Confusion Matrix (Block as Positive)

| Cell | Count |
|---|---:|
| TN | 113637 |
| FP | 407 |
| FN | 2699 |
| TP | 1365 |

## Route Distribution

| Status | Count |
|---|---:|
| Approve | 73817 |
| Flag | 42519 |
| Block | 1772 |
