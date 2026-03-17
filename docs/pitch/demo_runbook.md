# Demo Runbook (Preliminary + Backup)

## Before Recording
1. Start backend with local Ollama timeout that is long enough for generation.
2. Confirm `curl http://127.0.0.1:8000/health` returns all `true`.
3. Open the Streamlit dashboard.
4. Set recovery message mode to `Richer wording`.
5. Use exact saved cases, not the sparse manual form, for the main recording.

## Primary Flow
1. Show `/health` readiness for model, feature store, and Ollama.
2. Send exact `Approve` case and show fast low-risk routing.
3. Send exact `Flag` case and show local chat-style message generation.
4. Send exact `Block` case and explain why the system hard-stops only the highest-confidence fraud.

## Talking Points During Demo
- `Approve` and `Block` stay on the fast model path.
- `Flag` is slower in `Richer wording` mode because it adds richer local explanation.
- The same `Flag` route can switch to `Faster wording` mode, which uses a deterministic local template for lower latency.
- The right-side chat panel shows the latest flagged conversation, not necessarily the latest transaction on the left.
- Thresholds are calibrated on validation data, not fixed magic numbers.

## Backup Strategy
- If Ollama is unavailable: show the deterministic fallback explanation and state that the decision path still works.
- If local generation is too slow for the live environment: switch the dashboard to `Faster wording` before recording.
- If the dashboard fails: call `/predict` directly and show the API JSON.
- If the network is unstable: run frontend and backend on the same machine.
- Keep one short prerecorded demo clip as disaster backup.
