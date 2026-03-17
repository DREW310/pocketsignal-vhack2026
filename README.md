# PocketSignal

PocketSignal is the product built by Team Cache Me for V-HACK 2026 Case Study 2 (Digital Trust - Real-Time Fraud Shield for the Unbanked).

## Why this repo exists
- Build a complete, free-to-run fraud triage pipeline with reproducible evidence.
- Demonstrate a working prototype with calibrated `Approve / Flag / Block` routing.
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
- `docs/`: case-study alignment, privacy notes, and business context

## Included reproducibility artifacts
- `artifacts/model_bundle.pkl` lets judges and teammates run the API and dashboard without retraining first.
- `reports/metrics.json` and `reports/demo_cases.json` feed the dashboard hero metrics and exact demo path.
- `reports/latency_judge_demo.md` and `reports/latency_fast_route.md` document the two local recovery trade-offs.

## Data access note
- This public repository does not redistribute Kaggle raw CSV files.
- Download the IEEE-CIS files into the project root before running preprocessing or retraining.
- Cache folders such as `__pycache__/`, `.DS_Store`, and `catboost_info/` are intentionally excluded.

## Quick start
1. Install dependencies

macOS / Linux:
```bash
python3 -m pip install -r requirements.txt
```

Windows PowerShell:
```powershell
py -3 -m pip install -r requirements.txt
```

2. Optional preprocessing run (sample mode)

macOS / Linux:
```bash
python3 scripts/preprocess.py --sample-frac 0.10
```

Windows PowerShell:
```powershell
py -3 scripts/preprocess.py --sample-frac 0.10
```

3. Train and export the model bundle

macOS / Linux:
```bash
python3 scripts/train.py --sample-frac 0.10
```

Windows PowerShell:
```powershell
py -3 scripts/train.py --sample-frac 0.10
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

5. Install and warm the local LLM (optional for richer wording mode)

macOS / Windows:
```bash
ollama pull llama3
```

For a lighter richer-wording benchmark, Final-round candidates include:
- `ollama pull llama3.2:1b`
- `ollama pull qwen2.5:1.5b`

6. Start FastAPI backend

macOS / Linux:
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

Windows PowerShell:
```powershell
$env:PYTHONPATH="src"
$env:POCKETSIGNAL_OLLAMA_TIMEOUT="8"
py -3 -m uvicorn apps.fastapi_app:app --host 0.0.0.0 --port 8000
```

7. Start Streamlit dashboard

macOS / Linux:
```bash
streamlit run apps/dashboard.py
```

Windows PowerShell:
```powershell
py -3 -m streamlit run apps/dashboard.py
```

8. Run latency tests (evidence)
```bash
python3 scripts/load_test.py --scenario mixed_exact --requests 60 --concurrency 3 --timeout 10 --response-profile judge_demo --output reports/latency_judge_demo.md
python3 scripts/load_test.py --scenario mixed_exact --requests 60 --concurrency 3 --timeout 10 --response-profile fast_route --output reports/latency_fast_route.md
```

9. Find demo-friendly transactions
```bash
python3 scripts/find_demo_cases.py --sample-frac 0.02
```
This writes `reports/demo_cases.json` with one candidate each for `Approve`, `Flag`, and `Block`.

## Cross-platform demo note
- Judges and teammates do not need to retrain the model to run the demo.
- The public repo includes `artifacts/model_bundle.pkl`, `reports/metrics.json`, and `reports/demo_cases.json`.
- That means a Windows teammate can install dependencies, start FastAPI and Streamlit, and run the same exact demo cases without redoing training first.
- If Ollama is unavailable on a teammate laptop, the system can still demonstrate the `Flag` route by switching to the faster deterministic local wording path.

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

## Key evidence files
- `reports/metrics_report.md`
- `reports/metrics.json`
- `reports/leakage_check.md`
- `reports/ablation_report.md`
- `reports/latency_judge_demo.md`
- `reports/latency_fast_route.md`
- `reports/latency_submission_summary.md`
- `docs/case_study2_compliance.md`
- `docs/privacy_and_ethics.md`
