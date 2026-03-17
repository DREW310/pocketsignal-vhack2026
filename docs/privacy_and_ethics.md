# Privacy and Ethics Controls

## Privacy-First Architecture
- Fraud model inference runs locally from `artifacts/model_bundle.pkl`.
- Richer `Flag` explanations use a local Ollama endpoint only when the recovery mode calls for it.
- The same `Flag` route can switch to a faster deterministic wording mode without sending data outside the partner environment.
- No OpenAI API integration exists in this repository.

## Data Minimization
- API accepts transaction fields needed for risk scoring and explanation routing.
- The system does not require a third-party cloud LLM to return a user-facing recovery step.
- Public repo artifacts exclude the raw Kaggle CSV files.

## Explainability
- Every `/predict` response includes a route, a risk score, and human-readable risk reasons.
- `top_features` are mapped into semantic reasons rather than raw technical feature names.
- The `Flag` recovery text can use richer local wording or faster deterministic wording depending on deployment needs.

## Accessibility and Localization
- Low-literacy mode now changes the confirmation wording itself into shorter, simpler language.
- `Flag` explanations support English and Bahasa Melayu.
- This matches a Malaysia-first pilot story while staying relevant to broader ASEAN wallet deployment.

## Human-In-The-Loop Recovery
- `Flag` is not treated as a final fraud verdict.
- The prototype now supports explicit user confirmation or denial in the recovery panel.
- A denial path records a blocked-and-escalated outcome rather than silently failing.

## Fairness and Bias Handling
- Monitor route mix, false positives, and approve-bucket fraud rate over time.
- Recalibrate thresholds when the gray zone grows too large or segment drift becomes visible.
- Review outcomes by user segment, device mix, and payment context before production deployment.
