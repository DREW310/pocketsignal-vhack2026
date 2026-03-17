# PocketSignal Ablation Report

Generated: 2026-03-10T13:41:45.529358Z

| Variant | PR-AUC | Recall@Block | FPR@Block | Notes |
|---|---:|---:|---:|---|
| baseline_no_graph_no_balance | 0.410515 | 0.148571 | 0.000698 | No graph features, no imbalance handling, no ensemble. |
| plus_imbalance_no_graph | 0.406436 | 0.142857 | 0.000873 | Added class imbalance handling only. |
| full_graph_plus_ensemble | 0.405421 | 0.148571 | 0.000698 | Graph features + imbalance + optional ensemble. |
