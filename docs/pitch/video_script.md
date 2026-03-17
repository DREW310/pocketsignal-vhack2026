# Preliminary Video Script (5-10 Minutes)

Use this as a direct speaking script. It is written for 4 speakers and matches the current PocketSignal prototype.

## Total Length Target

`8:00` to `9:00` minutes

## Speaker Split

- Speaker 1: team intro, problem, why Case Study 2
- Speaker 2: solution and technical architecture
- Speaker 3: model evidence and live demo
- Speaker 4: business model, competitors, roadmap, close

## 0:00-0:25 | Slide 1 | Team Intro

**Speaker 1**

"Hello judges, we are Cache Me, a team of four final-year AI students. For V-HACK 2026, we chose Case Study 2: Digital Trust - Real-Time Fraud Shield for the Unbanked. Our solution is PocketSignal, a privacy-first fraud triage layer for digital wallets and super apps."

## 0:25-1:10 | Slide 2 | Problem and Stakes

**Speaker 1**

"In ASEAN, digital wallet adoption is rising quickly, but trust is not rising at the same speed. For gig workers and rural micro-merchants, wallet balance is not optional money. It is working capital. One fraudulent debit can directly affect transport, food, or inventory, while one false positive can block a legitimate earning."

"This is why we did not design only a fraud detector. We designed a real-time fraud decision and recovery workflow."

## 1:10-1:45 | Slide 3 | Why We Chose Case Study 2

**Speaker 1**

"We chose Case Study 2 because it combines technical depth with social impact. The challenge is not only anomaly detection. The real challenge is detecting fraud fast enough for live wallet transactions, keeping false positives low, and communicating clearly to users who may have low digital literacy."

## 1:45-3:00 | Slide 4 | Solution Overview

**Speaker 2**

"PocketSignal works in three steps. First, we score the transaction using behavior features and contextual graph features. Second, we route it into one of three actions: Approve, Flag, or Block. Third, only the gray-zone Flag case triggers a local chat-style confirmation message."

"This architecture is intentional. Approve and Block stay fast because they use only the tree-model scoring path. For the gray zone, we support two local explanation modes: a richer wording mode for demos and user experience, and a faster deterministic wording mode for stricter latency targets."

"Most importantly, our explanation layer is fully local. We do not send financial data to OpenAI or any paid cloud LLM. The same recovery flow can be delivered in simple English or Bahasa Melayu."

## 3:00-4:10 | Slide 5 | Technical Architecture

**Speaker 2**

"For training, we merged IEEE-CIS transaction and identity tables on TransactionID. We engineered three feature families."

"First, behavioral profiling: historical card usage count, average amount, and time-derived patterns."

"Second, contextual graph features: we used NetworkX to model relationships between card1, DeviceInfo, and P_emaildomain. This helps surface shared infrastructure and suspicious clusters."

"Third, calibrated routing: instead of showing a raw fraud probability, we calibrate a risk score and then persist validation-derived route thresholds in the model bundle."

"Our API is built with FastAPI, our dashboard is in Streamlit, and our local explanation path uses Ollama with llama3."

## 4:10-5:00 | Slide 6 | Model Evidence

**Speaker 3**

"On our current full-data validation run, PocketSignal achieved a ROC-AUC of 0.9006 and a PR-AUC of 0.5007. The high-confidence Block lane reached 92.6 percent precision with a 0.0386 percent false-positive rate. At the same time, the Approve bucket stayed at only 0.169 percent fraud rate."

"This is the key idea: we keep the hard-block lane small and precise, while the gray zone becomes a confirmation workflow instead of a silent rejection."

"In our ablation study, the full graph-plus-ensemble setup improved ranking quality and lowered approve-bucket risk, although precision-recall gains were mixed on smaller samples. So we present the graph layer as a meaningful contextual signal, not a magic claim."

## 5:00-6:30 | Slide 7 | Live Demo

**Speaker 3**

"Now we show the live prototype."

"First, we load an exact Approve case. The transaction is approved immediately with a low risk score."

"Second, we load an exact Flag case. This time the system does not hard block. Instead, it triggers a local chat-style message asking the user to confirm the payment. Notice that this explanation is generated locally through Ollama, and the same flow can support English or Bahasa Melayu. For stricter latency settings, the same route can switch to a deterministic local template mode without changing the overall decision logic."

"Third, we load an exact Block case. This is the high-confidence fraud route, so the system blocks it immediately."

"This demo shows the full loop: detect, route, and communicate."

## 6:30-7:20 | Slide 8 | Market and Business Model

**Speaker 4**

"PocketSignal is a B2B2C product. Our paying customers are digital wallets, super apps, payout platforms, and payment processors. Our protected end users are gig workers and micro-merchants."

"Our business model is simple: pilot integration fee, recurring platform fee based on monitored transaction volume, and optional on-prem deployment and localization support."

"We are not trying to replace every fraud stack. Our entry point is narrower: wallet ecosystems where trust recovery matters as much as fraud detection."

## 7:20-8:00 | Slide 9 | Competitive Advantage and Social Impact

**Speaker 4**

"Rules-only systems are fast but brittle. Generic fraud APIs can score risk, but they are often cloud-dependent and weak on user recovery. PocketSignal combines graph-aware scoring, calibrated triage, privacy-first local explanation, and low-literacy-friendly UX in one loop."

"That makes our solution both technically defensible and socially aligned with SDG 8.10. We protect digital trust so vulnerable users can keep using formal digital channels with less fear."

## 8:00-8:40 | Slide 10 | Roadmap and Close

**Speaker 4**

"In the next three months, we aim to move from prototype to pilot-ready deployment with one wallet partner, threshold monitoring, and a Bahasa Melayu language pack for Malaysia-based pilots. In six months, we add segment-specific rules and operator tooling. In twelve months, we expand to a multi-tenant ASEAN deployment model."

"PocketSignal is our answer to Case Study 2 because it does not stop at identifying fraud. It turns fraud signals into fast decisions, human-readable recovery, and privacy-first trust protection."

"Thank you."

## Delivery Rules

- Do not say fixed `70 / 90` thresholds. Say: "thresholds are calibrated on validation data."
- Do not claim `Flag < 1 second` unless you have a valid local latency report proving it.
- Do say that PocketSignal supports a richer local explanation mode and a faster local wording mode, depending on deployment constraints.
