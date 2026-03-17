# Preliminary Director Runbook (4 Speakers)

Use this as the recording master script for the Preliminary Round video.

This document is stricter than the normal pitch script:
- it assigns each section to one speaker
- it tells you when to pause
- it tells you when to cut to slides or the demo
- it keeps the wording aligned with the current working prototype and current metrics

## Recording Target

- Total target length: `8:15` to `9:00`
- Format: slides first, then live demo inside Slide 7, then close
- Product name: `PocketSignal`
- Team name: `Cache Me`

## Team Layout

- Speaker 1: intro, problem, user segment
- Speaker 2: product flow, architecture
- Speaker 3: validation evidence, live demo
- Speaker 4: business model, competitive advantage, roadmap, closing

## General Delivery Rules

- Speak at about `85%` of normal conversation speed.
- Keep eye contact with the camera for opening and closing lines.
- Pause for `0.5` to `1.0` second after each metric-heavy sentence.
- Do not say fixed `70 / 90` thresholds.
- Say: `our thresholds are calibrated on validation data`.
- Do not promise `Flag under one second`.
- Say: `PocketSignal supports a richer local explanation mode and a faster local wording mode, depending on deployment constraints.`

## Slide 1 | Title | 0:00-0:30

### On screen
- Slide 1 title: `PocketSignal`
- Subtitle: privacy-first fraud triage layer
- Footer: `Team Cache Me`

### Speaker
- Speaker 1

### Script
"Good [morning/afternoon], judges. We are Cache Me, a team of four final-year AI students. Our product is PocketSignal, a privacy-first fraud triage layer for digital wallets and super apps."

"For V-HACK 2026, we chose Case Study 2 because it asks a harder question than simple fraud classification. The real challenge is how to detect risk quickly, reduce false positives, and still communicate clearly to vulnerable users."

### Direction
- Start on camera for the first sentence.
- Cut to Slide 1 on `Our product is PocketSignal`.
- Short pause before the second paragraph.

### Handoff line
"So first, let us explain why this problem matters in the first place."

## Slide 2 | Problem | 0:30-1:10

### Speaker
- Speaker 1

### Script
"In ASEAN wallet ecosystems, balance is often not spare cash. For gig workers and micro-merchants, it is working capital. It pays for transport, inventory, and day-to-day operations."

"Because of that, one fraudulent debit is damaging. But one false positive can also be damaging, because it blocks a real payment at the wrong moment. So we did not design only a fraud detector. We designed a trust-preserving decision workflow."

### Direction
- Stay on Slide 2 throughout.
- Pause briefly after `working capital`.
- Emphasize `one false positive can also be damaging`.

### Handoff line
"With that in mind, the next question is who exactly we are trying to protect."

## Slide 3 | User and Market | 1:10-1:55

### Speaker
- Speaker 1

### Script
"Our protected users are gig workers receiving wallet payouts and small merchants relying on QR or wallet-based payments. These are users who may be new to digital finance, or who may not feel confident resolving fraud alerts on their own."

"At the same time, our paying customers are wallet providers, super apps, payout platforms, and payment processors. We use the Philippines as our first market story because inclusion is improving there, but the trust gap is still real. According to Bangko Sentral ng Pilipinas, account ownership reached 65 percent in 2022, yet 34.3 million adults were still unbanked."

"That is why recovery and communication matter just as much as scoring."

### Direction
- Stay on Slide 3.
- Pause after the BSP statistic.
- End this section a little slower.

### Handoff line
"So now let us show how PocketSignal responds once a transaction enters the system."

## Slide 4 | Product Flow | 1:55-2:45

### Speaker
- Speaker 2

### Script
"PocketSignal works in three steps. First, it scores the transaction. Second, it routes the transaction into one of three actions: Approve, Flag, or Block. Third, only the gray-zone Flag case triggers a human-readable explanation."

"That design is deliberate. Approve and Block stay on the fast model path. For the gray zone, we support two local explanation modes: a richer wording mode for better user communication, and a faster deterministic wording mode for tighter latency constraints."

"Just as importantly, that explanation is generated locally. We do not send sensitive financial data to OpenAI or any external paid LLM API."

### Direction
- Use Slide 4 with a simple 3-lane diagram.
- Pause after `Approve, Flag, or Block`.
- Stress `generated locally`.

### Handoff line
"Once that product logic was clear, we built the technical stack around it."

## Slide 5 | Technical Architecture | 2:45-3:50

### Speaker
- Speaker 2

### Script
"For training, we use the IEEE-CIS fraud dataset by joining the transaction and identity tables on TransactionID. From there, we engineer three families of signals."

"First, behavioral profiling. This includes time-derived features, historical usage count, and past average amount. Second, contextual graph features. We connect card1 to DeviceInfo and P_emaildomain using NetworkX, which helps surface suspicious shared infrastructure. Third, we pass these signals into a LightGBM and CatBoost ensemble, then calibrate the output into a usable routing score."

"For deployment, the model bundle is served through FastAPI. The user-facing prototype runs in Streamlit. And for Flag transactions only, we generate a local chat-style confirmation message through Ollama and llama3."

### Direction
- Stay on Slide 5.
- If possible, animate arrows left to right as each stage is mentioned.
- Pause after `three families of signals`.

### Handoff line
"Of course, architecture only matters if the model is actually performing well, so next we show the evidence."

## Slide 6 | Validation Evidence | 3:50-4:45

### Speaker
- Speaker 3

### Script
"On our current full-data validation run, PocketSignal achieved a ROC-AUC of 0.9006 and a PR-AUC of 0.5007."

[pause]

"For the high-confidence Block lane, precision reached 92.6 percent, while the false-positive rate stayed at 0.0386 percent."

[pause]

"At the same time, the Approve bucket stayed at only 0.169 percent fraud rate. So in practice, we keep hard blocking narrow and precise, while the uncertain middle becomes a recovery workflow instead of a silent rejection."

"We also ran ablation. The full graph-plus-ensemble setup improved ranking quality and lowered approve-bucket risk, although smaller-sample precision-recall gains were mixed. So we present graph features as a meaningful contextual signal, not as a magic claim."

### Direction
- Keep Slide 6 static and clean.
- Pause after each metric line.
- Do not rush the last sentence.

### Handoff line
"With that evidence in place, we can now show the system live."

## Slide 7 | Live Demo Intro | 4:45-5:00

### Speaker
- Speaker 3

### Script
"For the demo, we use exact saved cases rather than sparse manual input, so the output is reproducible."

### Direction
- Stay on Slide 7 for one line only.
- Then cut to terminal for `/health`.

## Demo Block | 5:00-6:45

### Demo setup
- Screen 1: terminal ready with `/health`
- Screen 2: Streamlit dashboard already open
- `Richer wording` recovery mode selected
- Exact demo controls visible
- Keep the main recording in English; if time permits, show one short Bahasa Melayu Flag message as a bonus shot

### Demo Part A | `/health`

#### Speaker
- Speaker 3

#### Script
"Before we run any case, we first confirm that the model, feature store, and local Ollama service are all ready."

#### Direction
- Show terminal with:
  - `curl http://127.0.0.1:8000/health`
- Hold for `2` seconds so judges can read all `true`.
- Cut back to dashboard.

### Demo Part B | `Approve`

#### Speaker
- Speaker 3

#### Script
"First, this is our exact Approve case."

[click `Approve`]

"The transaction is routed immediately as low risk. There is no unnecessary interruption, and there is no chat escalation because the model is confident that this belongs on the safe path."

#### Direction
- Wait until the `Approve` badge appears.
- Hold for `2` seconds on the low latency line.

### Demo Part C | `Flag`

#### Speaker
- Speaker 3

#### Script
"Next, this is our exact Flag case."

[click `Flag`]

"Here, the system does not hard block the payment. Instead, it escalates into a local chat-style confirmation flow. This is where PocketSignal protects trust. When confidence is uncertain, the user gets a clear, simple message rather than an opaque rejection."

"And importantly, this explanation is generated locally through Ollama, not through an external paid API."

"For stricter latency settings, we also support a faster deterministic local template mode, but for this demo we are showing the richer local explanation path."

"Because this hackathon is hosted in Malaysia and our team is Malaysian, we also prepared a Bahasa Melayu version of the same recovery flow."

#### Direction
- Wait for the new flagged message to appear before continuing.
- Hold on the phone panel for `3` seconds.
- If the message is still generating, stay quiet until it renders.
- If fallback appears, continue anyway and say: `The recovery path still works locally even when generation falls back to a deterministic template.`

### Demo Part D | `Block`

#### Speaker
- Speaker 3

#### Script
"Finally, this is our exact Block case."

[click `Block`]

"This is the high-confidence fraud lane, so the system intervenes immediately. In other words, the product can approve normal activity, escalate the gray zone, and hard-stop the highest-confidence fraud."

#### Direction
- Hold for `2` seconds after the `Block` badge appears.
- Do not comment on the right chat panel unless asked; it still shows the latest flagged conversation by design.

### Demo close

#### Speaker
- Speaker 3

#### Script
"So that is the full decision loop: detect, route, and communicate."

### Handoff line
"Now that we have shown the live system, let us explain how this becomes a real product."

## Slide 8 | Business Model | 6:45-7:25

### Speaker
- Speaker 4

### Script
"PocketSignal is a B2B2C infrastructure product. Our direct customers are digital wallet providers, super apps, payout platforms, and payment processors. The end users we protect are gig workers and micro-merchants."

"Our business model is straightforward: a pilot integration fee, a recurring fee based on monitored transaction volume, and optional enterprise support for on-prem deployment or localization. We are not trying to replace every fraud stack. Our entry point is narrower and more practical: wallet ecosystems where trust recovery matters as much as fraud detection."

### Direction
- Slide 8 only.
- Keep the tone commercial, not technical.

### Handoff line
"That focused entry point is also what makes our competitive position clearer."

## Slide 9 | Competitive Advantage | 7:25-8:00

### Speaker
- Speaker 4

### Script
"Rules-only systems are fast, but they are brittle. Generic fraud APIs can score risk, but they are often cloud-dependent and weak on user recovery."

"PocketSignal combines graph-aware scoring, calibrated triage, privacy-first local explanation, and low-literacy-friendly messaging in one loop. So our advantage is not just that we classify fraud. Our advantage is that we make the right intervention and explain it in a way the user can act on."

### Direction
- Pause after `brittle`.
- Point visually to the comparison table if present.

### Handoff line
"Finally, we want to show that this can grow beyond a hackathon prototype."

## Slide 10 | Roadmap and Close | 8:00-8:40

### Speaker
- Speaker 4

### Script
"Over the next three months, our goal is to make PocketSignal pilot-ready with one wallet partner, threshold monitoring, and a Bahasa Melayu language pack for Malaysia-based pilots. By six months, we would add segment-specific policies and operator tooling. By twelve months, we would evolve into a multi-tenant ASEAN trust layer."

"To close, PocketSignal does not just detect fraud. It protects digital trust through fast decisions, clear user communication, and local privacy-first inference."

"Thank you."

### Direction
- Stay on Slide 10.
- End on the product line, then short pause, then `Thank you`.

## Backup Lines If Something Goes Wrong

### If the Flag message is slow
"The richer explanation lane is intentionally slower because it runs only for gray-zone transactions and stays fully local."

### If the right panel still shows the earlier Flag after a Block
"The right panel keeps the latest flagged conversation on screen. The current transaction decision is shown in the decision stream on the left."

### If the dashboard glitches
"The underlying API is still running, so we can continue from the FastAPI response directly."

## Final Recording Order

1. Record Slide 1 to Slide 6 cleanly.
2. Record the demo block in one take if possible.
3. Record Slide 8 to Slide 10.
4. Re-record only the demo block if timing or latency becomes awkward.

## Hard Rules For Accuracy

- Do not say `fixed thresholds`.
- Do say `calibrated thresholds`.
- Do not say `Flag is under one second`.
- Do say `PocketSignal supports richer local wording and faster local wording, depending on deployment constraints`.
- Do not claim graph features improved every metric.
- Do say `graph-aware features improved ranking quality and reduced approve-bucket risk in ablation`.
