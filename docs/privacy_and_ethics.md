# Privacy and Ethics Controls

## Privacy-First Architecture
- Fraud model inference runs locally from `artifacts/model_bundle.pkl`.
- LLM explanation uses local Ollama endpoint (`http://127.0.0.1:11434`) only when status is `Flag` and the response profile is set to richer local wording.
- The same Flag route can also use a deterministic local template mode for lower latency without sending data outside the partner environment.
- No OpenAI API integration exists in this repository.

## Data Minimization
- API accepts only transaction fields needed for risk scoring.
- Logs should avoid storing full PII and should redact free-text fields.

## Explainability
- Response includes human-readable risk reasons and plain-language explanation.
- SHAP or model feature importance artifacts are retained for audit.

## Accessibility and Localization
- The dashboard includes a low-literacy mode for shorter, simpler phrasing.
- Flag explanations support English and Bahasa Melayu, reflecting ASEAN localization needs and the team's Malaysian deployment context.

## Fairness and Bias Handling
- Monitor false positives by route and segment.
- Keep monthly review cadence for drift checks and threshold recalibration.
