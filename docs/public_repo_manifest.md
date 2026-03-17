# Public Repo Manifest

Use this as the final GitHub packaging checklist before Preliminary submission.

## Recommended repo name

- `pocketsignal-vhack2026`

Alternative if you want the team name included:

- `cache-me-pocketsignal`

The cleaner choice is `pocketsignal-vhack2026` because:
- the product should be the public-facing identity
- `Cache Me` can still appear in the README, slides, and video
- judges will understand the repository purpose immediately

## Must include in the public repo

### Root files
- `.gitignore`
- `Makefile`
- `README.md`
- `config.yaml`
- `requirements.txt`
- `references.md`

### Application code
- `apps/dashboard.py`
- `apps/fastapi_app.py`
- `src/payung/`
- `src/aegis_trust/`

Keep `src/aegis_trust/` because it preserves compatibility with the saved model bundle and earlier imports.

### Scripts
- `scripts/preprocess.py`
- `scripts/train.py`
- `scripts/run_ablation.py`
- `scripts/find_demo_cases.py`
- `scripts/load_test.py`
- `scripts/predict_sample.py`

### Tests
- `tests/test_explanations.py`
- `tests/test_preprocess.py`
- `tests/test_routing.py`

### Judge-run artifacts
- `artifacts/model_bundle.pkl`

### Required evidence reports
- `reports/metrics.json`
- `reports/metrics_report.md`
- `reports/demo_cases.json`
- `reports/leakage_check.md`
- `reports/ablation_report.md`
- `reports/ablation_report.json`
- `reports/data_profile.md`
- `reports/latency_judge_demo.md`
- `reports/latency_fast_route.md`
- `reports/latency_submission_summary.md`

### Required docs
- `docs/case_study2_compliance.md`
- `docs/rubric_matrix.md`
- `docs/privacy_and_ethics.md`
- `docs/execution_checklist.md`
- `docs/anti_plagiarism_protocol.md`
- `docs/streamlit_secrets_example.toml`
- `docs/business/market_and_impact.md`
- `docs/business/sustainability_and_cost.md`
- `docs/business/competitive_advantage.md`
- `docs/business/roadmap_3_6_12.md`
- `docs/pitch/preliminary_slide_contents.md`
- `docs/pitch/preliminary_canva_copy.md`
- `docs/pitch/video_script.md`
- `docs/pitch/preliminary_director_runbook.md`
- `docs/pitch/demo_runbook.md`
- `docs/pitch/judge_qna.md`
- `docs/pitch/architecture_diagram_content.md`

## Must not include in the public repo

### Kaggle raw competition data
- `train_transaction.csv`
- `train_identity.csv`
- `test_transaction.csv`
- `test_identity.csv`
- `sample_submission.csv`

### Local caches and generated junk
- `__pycache__/`
- `.DS_Store`
- `catboost_info/`

### Unrelated scratch material
- `skills/`
- `reports/citic_review_context.json`
- `reports/citic_review_context.md`
- `reports/citic_review_context_revised.json`
- `reports/citic_review_context_revised.md`
- `reports/citic_review_context_revised2.json`
- `reports/citic_review_context_revised2.md`
- `reports/citic_revised2_text.txt`
- `reports/citic_revised3_pdf.txt`
- `reports/citic_revised_text.txt`
- `reports/citic_revision_pack.md`
- `reports/aip_template_text.txt`

### Optional local-only file
- `artifacts/processed_sample.csv`

This file is not required for the demo or the rubric and should stay out of the public repo.

## GitHub submission standard

Before you submit:

1. Make sure the repo is `Public`.
2. Confirm the raw Kaggle CSV files are not tracked.
3. Confirm `artifacts/model_bundle.pkl`, `reports/metrics.json`, and `reports/demo_cases.json` are tracked.
4. Confirm the README explains what PocketSignal does, how to run it, and what evidence files matter.
5. Confirm the video link works.

## Why this packaging matters

Judges are not only scoring code quality. They are also scoring:
- reproducibility
- technical clarity
- business clarity
- delivery discipline

A public repo that is clean, minimal, and runnable scores better than a noisy repo that contains raw datasets, unrelated scratch files, or missing judge-facing artifacts.
