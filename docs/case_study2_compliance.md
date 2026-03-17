# Case Study 2 Compliance Checklist

## Requirement Mapping

| Requirement | Implementation Evidence | Completion Criteria |
|---|---|---|
| Behavioral Profiling | `src/payung/preprocess.py` (`card1_txn_count_past`, `card1_amt_mean_past`) | Report with feature values and leakage-safe logic |
| Real-Time Anomaly Scoring | `apps/fastapi_app.py` `/predict` + route logic | API returns `Approve/Flag/Block` with risk score |
| Imbalanced Class Handling | `src/payung/modeling.py` (`scale_pos_weight` / balanced mode) | Metrics report shows fraud recall/precision trade-off |
| Contextual Data Integration | `src/payung/preprocess.py` graph degree features | Ablation report quantifies uplift |
| Low Latency | `scripts/load_test.py`, `reports/latency_judge_demo.md`, `reports/latency_fast_route.md`, configurable `response_profile` in API | `Flag` supports both rich local-LLM mode and fast deterministic local mode, with separate evidence for each |
| False Positive Control | threshold optimization in `modeling.py` + metrics report | Controlled FPR at block route |
| Privacy-First | local Ollama client (`src/payung/llm.py`) only for `Flag` | No external OpenAI call in code path |
| Deliverables (Engine + API) | `scripts/train.py`, `apps/fastapi_app.py` | model bundle + running API demo |

## Free-Only Confirmation
- All dependencies are open-source and free for local use.
- Local LLM via Ollama avoids paid API calls.
- Public submission artifacts can be hosted on free GitHub and YouTube tiers.
