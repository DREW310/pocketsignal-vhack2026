# PocketSignal Latency Submission Summary

## Why There Are Two Latency Reports

PocketSignal supports two local recovery modes for the `Flag` route:
- **Richer local wording**: better user-facing recovery text through local Ollama generation
- **Faster local wording**: deterministic local wording for stricter latency settings

This is an intentional deployment trade-off, not a measurement inconsistency.

## Current Local Mixed Exact-Case Results

### Richer local wording (`response_profile=judge_demo`)
- `Approve p95`: `96.976 ms`
- `Flag p95`: `4574.600 ms`
- `Block p95`: `72.341 ms`
- `Error count`: `0`

Reading:
- best for demo clarity and richer on-screen recovery wording
- the gray-zone `Flag` path is slower because it includes local generation

### Faster local wording (`response_profile=fast_route`)
- `Approve p95`: `113.324 ms`
- `Flag p95`: `110.790 ms`
- `Block p95`: `130.708 ms`
- `Error count`: `0`

Reading:
- best for deployment-oriented latency discussion
- all three routes stayed within roughly `131 ms` p95 in the current mixed exact-case local run

## Judge-Safe Summary

Use this exact wording in slides or speech:

"PocketSignal supports two local recovery modes. The richer local wording mode gives better demo-quality user messaging but a slower gray-zone path. The faster local wording mode keeps all three routes close to real-time in our current mixed exact-case local benchmark, with no request errors in the run."
