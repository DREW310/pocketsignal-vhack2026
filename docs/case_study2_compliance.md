# Case Study 2 Compliance Checklist

## Requirement Mapping

| Requirement | Implementation Evidence | Completion Criteria |
|---|---|---|
| Behavioral Profiling | `src/payung/preprocess.py` (`card1_txn_count_past`, `card1_amt_mean_past`) | Leak-safe historical behavior signals are present in both training and inference |
| Real-Time Anomaly Scoring | `apps/fastapi_app.py` `/predict` + calibrated routing bundle | API returns `Approve / Flag / Block` with risk score, probability, explanation, and latency |
| Imbalanced Class Handling | `src/payung/modeling.py` (`scale_pos_weight`, calibrated evaluation) | Validation report shows rare-class precision/recall trade-offs |
| Contextual Data Integration | `src/payung/preprocess.py` graph degree features | Shared device and email context are included in the scoring layer |
| Low Latency | `scripts/load_test.py`, `reports/latency_judge_demo.md`, `reports/latency_fast_route.md` | Faster local wording mode kept all three routes at about `131 ms p95` or below in the current mixed exact-case local run |
| False Positive Control | threshold optimization in `modeling.py` + `reports/metrics_report.md` | Narrow `Block` lane with controlled false positives |
| Privacy-First | local Ollama client (`src/payung/llm.py`) only for richer `Flag` wording | No external paid LLM API in the code path |
| Deliverables (Engine + API) | `scripts/train.py`, `apps/fastapi_app.py`, `apps/dashboard.py` | trained bundle + working API + reproducible demo cases |
| Closed-Loop Recovery | `apps/dashboard.py` confirm / deny loop | `Flag` can resolve into user-confirmed or user-denied outcomes on-screen |

## What The Prototype Now Demonstrates

- most validation traffic stays on the `Approve` fast path
- the gray zone is materially smaller than the earlier conservative routing version
- the `Flag` route now supports a visible user confirmation loop instead of a static chat bubble
- low-literacy mode changes the wording itself, not just the message length
- only denied or unresolved flagged cases need manual follow-up; not every `Flag` becomes human review

## Free-Only Confirmation

- All dependencies are open-source and free for local use.
- Local LLM via Ollama avoids paid API calls.
- The prototype can run locally from the included model bundle without retraining first.
