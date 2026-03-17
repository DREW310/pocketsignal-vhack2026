# Judge Q&A Prep

Use this when judges ask follow-up questions after the demo.

## 1. Why did you not integrate directly with WhatsApp or Telegram?

Recommended answer:

"For the Preliminary Round, we prioritized a stable wallet-side prototype instead of a third-party messaging integration. The case study asks for a mock-up showing how a digital wallet would receive and act on a risk score, so our Streamlit interface already proves the product logic. A Telegram or WhatsApp integration is possible later, but it adds platform dependency, moderation, and API complexity without improving the core fraud decision quality."

## 2. Why do you call it a chat-style confirmation assistant instead of a WhatsApp bot?

Recommended answer:

"Because our product idea is not tied to a single messaging platform. The important part is the recovery workflow: when a transaction falls into the gray zone, the user gets a simple confirmation message in a familiar chat format. That can live inside a wallet app, a super app, or a partner messaging channel."

## 3. Is your model better than the original Kaggle competition winners?

Recommended answer:

"No. We are not claiming to beat the winning Kaggle leaderboard solutions. Our current full-data validation ROC-AUC is 0.9006, while the first-place IEEE-CIS Kaggle solution was reported at 0.9459 private leaderboard AUC. Our goal in this hackathon is different: strong model quality plus a deployable trust workflow, privacy-first local explanation, and a working risk API prototype."

## 4. So do you need to beat Kaggle benchmarks to score well here?

Recommended answer:

"Not necessarily. This hackathon is not a Kaggle leaderboard contest. Judges are scoring not only model performance, but also system integration, latency, privacy, scalability, accessibility, market fit, and delivery. So our target is not just a stronger classifier. It is a stronger end-to-end fraud shield."

## 5. Why do you report ROC-AUC and PR-AUC?

Recommended answer:

"ROC-AUC is useful because IEEE-CIS was historically evaluated with AUC, so it gives us benchmark continuity. PR-AUC matters because this is a highly imbalanced fraud dataset, and precision-recall behavior is more informative for rare positive cases. We use both so that ranking quality and minority-class usefulness are both visible."

## 6. Why did you not use SMOTE?

Recommended answer:

"We deliberately avoided SMOTE because synthetic fraud samples can distort structured financial behavior, especially when graph and temporal context matter. Instead, we used class-imbalance-aware tree models and calibrated routing, which is safer for this type of transaction data."

## 7. Why did you not use a graph neural network?

Recommended answer:

"For a student competition prototype, we chose graph-derived features rather than a full graph neural network because they are easier to explain, lighter to deploy, and faster to connect into a real-time API. That decision gave us a better balance between technical depth and production feasibility."

## 8. Why is the Flag path slower than Approve or Block?

Recommended answer:

"Because Approve and Block stay on the fast model path, while Flag can add a local language explanation step. That is a conscious architecture tradeoff. We only pay that latency cost for gray-zone cases, not for every transaction, and we already support a faster deterministic local template mode when latency matters more than richer wording."

## 9. If Flag is slower, is the system still real-time?

Recommended answer:

"Yes, for the core risk routing path. Our current exact-case measurements show the Approve and Block routes staying on the fast path, while Flag is a slower escalation path when we use richer local LLM wording. We also support a faster local template mode for stricter latency settings, so the product can trade off explanation richness against response speed without sending data outside the partner environment."

## 10. What makes this inclusive, not just accurate?

Recommended answer:

"Two things. First, we avoid hard blocking the entire gray zone, which reduces silent failure for legitimate users. Second, we translate risk into simple user-facing confirmation messages, including Bahasa Melayu support, instead of exposing raw model outputs or technical fraud scores."

## 11. What would you improve next if you reached the Final Round?

Recommended answer:

"We would focus on three upgrades: first, further optimize and benchmark the fast versus rich Flag explanation modes; second, enrich the explanation layer with more user-friendly semantic reasons; and third, strengthen localization and operator tooling for pilot deployment."

## 12. Your Block recall is relatively low. Why is that acceptable?

Recommended answer:

"Because our system is not designed as a single hard-block classifier. We intentionally keep the Block lane narrow and high-confidence, which is why Block precision is high and false positives are very low. The rest of the suspicious space is handled by the Flag route, where the system can escalate instead of silently declining legitimate users."

## 13. What is the strongest one-line summary of your product?

Recommended answer:

"PocketSignal does not just detect fraud. It decides the right intervention and communicates it in a privacy-first way that protects user trust."
