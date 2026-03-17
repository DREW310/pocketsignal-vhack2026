# Architecture Diagram Content

Use this document when drawing the system diagram in draw.io, Canva, Figma, or PowerPoint.

## Diagram Title

`PocketSignal - Privacy-First Real-Time Fraud Triage for the Unbanked`

## Layout Recommendation

Draw the architecture from left to right in 6 blocks:

1. Data
2. Feature Engineering
3. Model Training
4. Real-Time API
5. Local LLM Escalation
6. Front-End / User Response

## Box 1 - Data

### Header
`IEEE-CIS Fraud Detection Data`

### Body
- `train_transaction.csv`
- `train_identity.csv`
- Join key: `TransactionID`
- Target: `isFraud`

### Callout
`Identity data is missing for some rows, so the merge is LEFT JOIN.`

## Box 2 - Feature Engineering

### Header
`Behavior + Context Feature Layer`

### Body
- Time features from `TransactionDT`
  - `hour`
  - `day`
- Behavior features
  - `card1_txn_count_past`
  - `card1_amt_mean_past`
- Graph features
  - `card1_device_degree`
  - `card1_email_degree`

### Callout
`Graph features connect card usage to device and email context.`

## Box 3 - Model Training

### Header
`Fraud Scoring Engine`

### Body
- `LightGBM + CatBoost ensemble`
- Class imbalance handling
- Probability calibration
- Validation-based threshold persistence

### Metrics footer
- `ROC-AUC: 0.9006`
- `PR-AUC: 0.5007`
- `Precision@Block: 92.6%`

## Box 4 - Real-Time API

### Header
`FastAPI Risk API`

### Body
- `POST /predict`
- `GET /health`
- Returns:
  - `status`
  - `risk_score`
  - `probability`
  - `top_features`
  - `explanation`
  - `latency_ms`

### Callout
`Thresholds are calibrated on validation data and loaded from the model bundle.`

## Box 5 - Route Policy

### Header
`Three-Stage Triage`

### Body
- `Approve`
- `Flag`
- `Block`

### Small note
`Approve and Block stay on the fast model path.`

## Box 6 - Local LLM Escalation

### Header
`Flag-Only Local Explanation`

### Body
- `Ollama`
- `llama3`
- switchable richer / faster local wording
- local chat-style confirmation message
- English / Bahasa Melayu pack
- no OpenAI API

### Callout
`Only gray-zone transactions trigger the explanation layer; the system can use richer local wording or a faster local template without sending data to an external LLM API.`

## Box 7 - Front-End

### Header
`PocketSignal Dashboard`

### Body
- Live transaction stream
- chat-style assistant panel
- Low-literacy mode
- language selector
- Exact demo cases

## Box 8 - End User Outcome

### Header
`Wallet User Experience`

### Body
- Normal payments continue
- Suspicious payments ask for confirmation
- High-confidence fraud is blocked

## Connector Labels

Use these arrow labels between boxes:

- Data -> Feature Engineering:
  `merge, clean, enrich`

- Feature Engineering -> Model Training:
  `behavior + graph-aware signals`

- Model Training -> Real-Time API:
  `model bundle + calibrated thresholds`

- Real-Time API -> Route Policy:
  `risk score 0-100`

- Route Policy -> Local LLM Escalation:
  `Flag only`

- Route Policy -> Front-End:
  `Approve / Block decision`

- Local LLM Escalation -> Front-End:
  `friendly confirmation message`

- Front-End -> End User Outcome:
  `trust-preserving action`

## Bottom Banner Text

Add one footer line under the diagram:

`PocketSignal detects fraud, routes decisions in real time, and communicates clearly without sending sensitive data to an external LLM API.`

## What Not To Put In The Diagram

- Do not write fixed `70 / 90` thresholds.
- Do not claim cloud deployment if you are demoing local inference.
- Do not show OpenAI or any external paid API logos.
