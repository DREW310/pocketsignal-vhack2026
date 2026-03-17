# Leakage Check Report

Generated: 2026-03-17T08:47:24.835225+00:00

- Rows after merge: 590540
- Rows after preprocessing: 590540
- Target column included in feature set: False

## Notes
- Time-based split is used to avoid future leakage into earlier transactions.
- Historical card behavior features are based on past rows only (cumcount/cumsum pattern).
- Graph degree features are computed without using labels.
