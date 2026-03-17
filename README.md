# PocketSignal

PocketSignal is the product built by team Cache Me for V-HACK 2026 Case Study 2 (Digital Trust - Real-Time Fraud Shield for the Unbanked).

## Why this repo exists
- Build a complete, free-to-run fraud pipeline with reproducible evidence.
- Cover both Preliminary and Final round rubric requirements in one repository.
- Keep all sensitive data local (no OpenAI API usage).

## Tech stack (all free)
- Data/ML: pandas, scikit-learn, LightGBM, CatBoost, SHAP, NetworkX
- API: FastAPI + Uvicorn
- Dashboard: Streamlit
- Local LLM: Ollama (`llama3`) for Flag-case chat-style explanation in English or Bahasa Melayu

## Repository structure
- `config.yaml`: centralized experiment and routing configuration
- `src/payung/preprocess.py`: data merge + engineered features + feature store
- `src/payung/modeling.py`: model training, calibration, threshold optimization, evaluation
- `src/payung/inference.py`: online inference service logic
- `src/payung/llm.py`: Ollama local client and fallback behavior
- `apps/fastapi_app.py`: `/predict` and `/health` endpoints
- `apps/dashboard.py`: real-time dashboard with chat-style confirmation panel
- `scripts/preprocess.py`: data engineering run + profile report
- `scripts/train.py`: end-to-end train + metrics artifact generation
- `scripts/run_ablation.py`: ablation (graph / imbalance / ensemble)
- `scripts/load_test.py`: latency testing for Gate C
- `reports/`: generated technical reports
- `docs/`: rubric mapping, case compliance, business and pitch assets

## What belongs in the public repo
- Keep the source code, docs, markdown reports, and config files.
- Keep `artifacts/model_bundle.pkl` in the repo so judges can run the API and dashboard without retraining.
- Keep `reports/metrics.json` and `reports/demo_cases.json` in the repo because the dashboard reads them for the hero metrics and exact demo path.
- Do not commit Kaggle raw CSV files into a public GitHub repo.
- Do not commit cache folders such as `__pycache__/`, `.DS_Store`, or `catboost_info/`.
- Commit download instructions for IEEE-CIS instead of redistributing the raw competition files.
- For the exact include / exclude list, see `docs/public_repo_manifest.md`.

## Recommended screenshot set
- Add 3 to 5 screenshots to the GitHub repo and the submission deck.
- Use the capture plan in `docs/readme_screenshot_checklist.md`.
- Recommended examples:
  - product overview screen
  - exact `Approve` case
  - exact `Flag` case with recovery message
  - exact `Block` case
  - architecture diagram slide

## Quick start
1. Install dependencies:
```bash
python3 -m pip install -r requirements.txt
```

2. Run preprocessing (sample mode):
```bash
python3 scripts/preprocess.py --sample-frac 0.10
```

3. Train and export model bundle:
```bash
python3 scripts/train.py --sample-frac 0.10
```

If your local environment has OpenMP runtime issues, use:
```bash
python3 scripts/train.py --sample-frac 0.10 --safe-mode
```
This switches to a LogisticRegression fallback model for reproducible local delivery.

If LightGBM fails on macOS with `libomp.dylib` missing, install:
```bash
brew install libomp
```

4. (Optional) Run ablation study:
```bash
python3 scripts/run_ablation.py --sample-frac 0.05
```
Or safe fallback mode:
```bash
python3 scripts/run_ablation.py --sample-frac 0.05 --safe-mode
```

5. Start FastAPI backend:
```bash
PYTHONPATH=src uvicorn apps.fastapi_app:app --host 0.0.0.0 --port 8000
```

Useful demo-time environment options:
```bash
POCKETSIGNAL_RESPONSE_PROFILE=fast_route
POCKETSIGNAL_OLLAMA_KEEP_ALIVE=10m
POCKETSIGNAL_OLLAMA_PRELOAD=1
POCKETSIGNAL_OLLAMA_TIMEOUT=8
```

- `POCKETSIGNAL_RESPONSE_PROFILE=fast_route` makes the gray-zone recovery path use deterministic local wording by default.
- `POCKETSIGNAL_OLLAMA_KEEP_ALIVE=10m` keeps the richer local wording model resident between requests when supported by Ollama.
- `POCKETSIGNAL_OLLAMA_PRELOAD=1` attempts a best-effort warm preload on startup.
- `POCKETSIGNAL_OLLAMA_TIMEOUT=8` is a more realistic demo-time timeout than the strict low default used in development.

6. Start Streamlit dashboard:
```bash
streamlit run apps/dashboard.py
```

7. Run latency test (Gate C evidence):
```bash
python3 scripts/load_test.py --scenario mixed_exact --requests 60 --concurrency 3 --timeout 10 --response-profile judge_demo --output reports/latency_judge_demo.md
python3 scripts/load_test.py --scenario mixed_exact --requests 60 --concurrency 3 --timeout 10 --response-profile fast_route --output reports/latency_fast_route.md
```

8. Find demo-friendly transactions:
```bash
python3 scripts/find_demo_cases.py --sample-frac 0.02
```
This writes `reports/demo_cases.json` with one candidate each for `Approve`, `Flag`, and `Block`.

## API contract
`POST /predict`
- Input: transaction feature JSON (`TransactionAmt`, `card1`, `DeviceInfo`, ...)
- Output:
  - `status`: `Approve | Flag | Block`
  - `risk_score`: integer 0-100, mapped from the validation score distribution
  - `probability`: calibrated fraud probability
  - `top_features`: top model-driven factors
  - `explanation`: local explanation text (LLM only for `Flag`)
  - `preferred_language`: optional (`English | Bahasa Melayu`)
  - `response_profile`: optional (`judge_demo | fast_route`)
  - `latency_ms`
  - `model_version`

`GET /health`
- `model_loaded`
- `ollama_ready`
- `feature_store_ready`

## Routing policy
- `Approve`: score < calibrated `approve_threshold`
- `Flag`: `approve_threshold` <= score <= `block_threshold`
- `Block`: score > calibrated `block_threshold`

Thresholds are auto-optimized on validation data and persisted in the model bundle.
The current sample run writes the exact values into `reports/metrics_report.md` and `reports/metrics.json`.
The optimizer also enforces minimum `Approve`, `Flag`, and `Block` route shares to avoid degenerate runs where one bucket collapses.

## Flag explanation modes
- `judge_demo`: uses richer local Ollama wording when available and falls back to a deterministic local template if generation is unavailable
- `fast_route`: skips LLM generation and uses a deterministic local confirmation template for lower latency

Example latency command using fast local template mode:
```bash
python3 scripts/load_test.py --scenario mixed_exact --requests 60 --concurrency 3 --timeout 10 --response-profile fast_route
```

## Required evidence outputs
- `reports/metrics_report.md`
- `reports/metrics.json`
- `reports/leakage_check.md`
- `reports/ablation_report.md`
- `reports/latency_judge_demo.md`
- `reports/latency_fast_route.md`
- `reports/latency_submission_summary.md`
- `docs/rubric_matrix.md`
- `docs/case_study2_compliance.md`

## Anti-plagiarism evidence practices
- Keep daily commits per member.
- Keep timestamped experiment artifacts in `reports/`.
- Maintain source references in `references.md`.
- Demo full closed-loop flow: `Flag -> local LLM message -> user confirmation`.

## Submission note
- Preliminary submission does not require a public live deployment.
- The required delivery is a working prototype, a public GitHub source-code repository, and the recorded video pitch.
- For judge-facing stability, keep the working demo local and reproducible instead of adding a late external hosting dependency.
