# Preliminary Presentation Pack

This file gives you three things for each slide:
- exact on-slide copy
- natural speaking script
- short transition line into the next slide

Use this instead of improvising.

## Slide 1

### On-slide title
`PocketSignal`

### On-slide subtitle
`A privacy-first fraud triage layer for unbanked digital wallet users`

### On-slide footer
`V-HACK 2026 | Case Study 2 | Team Cache Me`

### Speaker script
"Good [morning/afternoon], judges. We are Cache Me, a team of four final-year AI students. For V-HACK 2026, we selected Case Study 2, which focuses on real-time fraud protection for unbanked users. Our solution is PocketSignal, a privacy-first fraud triage layer designed for digital wallets and super apps."

### Transition
"To explain why we built it this way, let us start with the problem itself."

## Slide 2

### On-slide title
`Why this problem matters`

### On-slide bullets
- Wallet balance is working capital
- Fraud destroys trust
- False positives also hurt earnings
- Detection alone is not enough

### Speaker script
"In this segment, wallet balance is not just convenience money. For many gig workers and micro-merchants, it is the money they use for transport, daily expenses, and business turnover. So when fraud happens, the loss is immediate. At the same time, false positives are also harmful, because a legitimate transaction can be blocked when the user needs it most. That is why we focused not only on fraud detection, but also on trust-preserving recovery."

### Transition
"Once we understood that, the next question was who exactly we are building for."

## Slide 3

### On-slide title
`Who we protect`

### On-slide bullets
- Gig workers receiving wallet payouts
- Rural and neighborhood micro-merchants
- Wallet providers and super apps as pilot customers
- Philippines-first market story

### Speaker script
"Our protected users are gig workers receiving wallet payouts and micro-merchants relying on QR or wallet-based payments. Meanwhile, our paying customers would be wallet providers, super apps, payout platforms, and payment processors. We use the Philippines as our first market story because financial inclusion is improving there, but trust is still fragile. Bangko Sentral ng Pilipinas reported that account ownership reached 65 percent in 2022, yet 34.3 million adults were still unbanked. That makes fraud trust and recovery a real adoption barrier, not a theoretical one."

### Transition
"So with that user in mind, this is how PocketSignal works."

## Slide 4

### On-slide title
`PocketSignal in one screen`

### On-slide bullets
- Score the transaction
- Route: Approve / Flag / Block
- Explain only the gray zone
- Keep all sensitive data local

### Speaker script
"PocketSignal has a simple idea. First, we score the transaction. Second, we route it into one of three actions: Approve, Flag, or Block. Third, only the gray-zone Flag route triggers a human-readable explanation. This matters because it keeps the fast path fast, while still giving the user a clear message when the system is uncertain. Just as importantly, that explanation is generated locally. We do not send sensitive financial data to an external paid LLM API."

### Transition
"Now let us unpack the technical stack behind that workflow."

## Slide 5

### On-slide title
`How the system works`

### On-slide bullets
- IEEE-CIS transaction + identity merge
- Behavior features
- Graph-aware context features
- LightGBM + CatBoost
- FastAPI + Streamlit + local Ollama

### Speaker script
"We trained PocketSignal on the IEEE-CIS fraud dataset by merging the transaction and identity tables on TransactionID. From there, we engineered three groups of signals. First, we used behavior features such as historical card usage frequency, past average amount, and time-derived patterns. Second, we added graph-aware context by connecting card1 to DeviceInfo and P_emaildomain using NetworkX. Third, we passed these signals into a LightGBM and CatBoost ensemble, and then exposed the model through FastAPI. On top of that, we built a Streamlit dashboard, and for flagged transactions only, we generate a local chat-style explanation through Ollama and llama3."

### Transition
"Of course, architecture only matters if the model is actually performing well, so let us look at the evidence."

## Slide 6

### On-slide title
`Validation evidence`

### On-slide bullets
- `ROC-AUC: 0.9006`
- `PR-AUC: 0.5007`
- `Precision@Block: 92.6%`
- `FPR@Block: 0.0386%`
- `Approve bucket fraud rate: 0.169%`

### On-slide footer
`Thresholds are calibrated on validation data.`

### Speaker script
"On our current full-data validation run, PocketSignal achieved a ROC-AUC of 0.9006 and a PR-AUC of 0.5007. More importantly for deployment, the high-confidence Block lane reached 92.6 percent precision with a 0.0386 percent false-positive rate. At the same time, the Approve bucket stayed at only 0.169 percent fraud rate. In other words, we reserve hard blocking for the most confident fraud cases, while the uncertain middle zone becomes a recovery workflow instead of a silent decline."

### Transition
"With that evidence in place, we can now show the live product."

## Slide 7

### On-slide title
`Live demo: detect, route, communicate`

### On-slide bullets
- Exact `Approve` case
- Exact `Flag` case
- Exact `Block` case
- Local chat-style explanation
- English / Bahasa Melayu support

### Speaker script
"For the demo, we use exact saved test cases so the output is reproducible. First, we load an Approve case, and the transaction goes through immediately with a low risk score. Next, we load a Flag case. Here, the system does not block the transaction right away. Instead, it generates a local chat-style confirmation message asking the user to verify the payment. That message can be delivered in simple English or Bahasa Melayu. Finally, we load a Block case, which is the high-confidence fraud lane. This sequence shows the full logic of PocketSignal: detect the risk, choose the right intervention, and communicate in a way the user can understand."

Optional presenter note:
"For stricter latency settings, the same Flag route can also switch to a deterministic local template mode. In this demo, we intentionally show the richer local wording path."

### Transition
"Now that the technical side is clear, let us look at how this becomes a real product."

## Slide 8

### On-slide title
`How this becomes a product`

### On-slide bullets
- B2B2C model
- Pilot setup fee
- Recurring fee by transaction volume
- Optional on-prem and localization support

### Speaker script
"PocketSignal is a B2B2C product. Our direct customers are digital wallet providers, super apps, payout platforms, and payment processors. The end users we protect are gig workers and micro-merchants. From a business standpoint, the model is straightforward: a pilot integration fee, a recurring fee tied to monitored transaction volume, and optional enterprise support for on-prem deployment or language localization. We are not trying to replace every fraud stack at once. Our entry point is much narrower and more practical: wallet ecosystems where trust recovery is as important as fraud detection."

### Transition
"That narrow entry point is also what gives us a clearer competitive story."

## Slide 9

### On-slide title
`Why PocketSignal is different`

### On-slide bullets
- Rules-only systems are fast but brittle
- Generic fraud APIs score risk but do not recover trust
- PocketSignal adds graph context, calibrated triage, and local messaging

### Speaker script
"Rules-only systems are fast, but they are brittle and easier to evade. Generic fraud APIs can score risk, but they often stay black-box, cloud-dependent, and weak on user recovery. PocketSignal combines graph-aware scoring, calibrated triage, privacy-first explanation, and low-literacy-friendly messaging in one loop. That matters because our advantage is not any single model. It is the entire decision-and-recovery workflow."

### Transition
"Finally, we want to show that this can grow beyond a hackathon prototype."

## Slide 10

### On-slide title
`Why this can grow beyond the hackathon`

### On-slide bullets
- 3 months: pilot-ready deployment
- 6 months: segment-specific policies
- 12 months: multi-tenant ASEAN expansion
- Privacy-first and low-cost by design

### Speaker script
"Over the next three months, our goal is to make PocketSignal pilot-ready with one wallet partner, route monitoring, and a Bahasa Melayu language pack for Malaysia-based pilots. By six months, we would add segment-specific policies and better tooling for fraud operators. By twelve months, we would evolve the system into a multi-tenant ASEAN trust layer. To close, PocketSignal does not just detect fraud. It protects digital trust through fast decisions, clear user communication, and local privacy-first inference. Thank you."

### Final close
"Thank you, judges. We are Cache Me, and this is PocketSignal."

## Demo-Specific Speaking Script

Use these exact lines during the product demo section.

### `/health`
"Before we show the cases, we first check that the model, feature store, and local Ollama service are all ready."

### `Approve`
"This first transaction is our exact Approve case. As expected, the system routes it immediately as low-risk."

### `Flag`
"Now we load an exact Flag case. Here the model is not fully confident, so instead of blocking, it generates a local chat-style confirmation message. This is important because it protects trust while still reacting in real time."

### `Block`
"Finally, this is our exact Block case. This is the high-confidence fraud path, so the system intervenes immediately."

### Demo close
"So in one workflow, PocketSignal can approve normal activity, escalate the gray zone, and block high-confidence fraud."

## Delivery Notes

- Speak slightly slower than normal conversation speed.
- Keep each sentence short.
- Pause after every metric-heavy sentence.
- Do not say fixed `70 / 90` thresholds.
- Do not promise `Flag < 1 second` unless a valid local latency report proves it.
