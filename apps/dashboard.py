"""PocketSignal demo dashboard for Team Cache Me.

This UI is intentionally demo-first:
- exact saved cases are the main judging path
- manual input is secondary and exploratory
- the right panel shows the latest flagged recovery conversation
"""

from __future__ import annotations

import json
import random
import re
import sys
import time
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import streamlit as st

DEFAULT_API_PREDICT_URL = "http://127.0.0.1:8000/predict"
FRONTEND_HTTP_TIMEOUT_SECONDS = 8.0
ROOT = Path(__file__).resolve().parents[1]
DEMO_CASES_PATH = ROOT / "reports" / "demo_cases.json"
METRICS_PATH = ROOT / "reports" / "metrics.json"
sys.path.insert(0, str(ROOT / "src"))

from payung.llm import fallback_flag_message


def resolve_api_predict_url() -> str:
    try:
        pocketsignal = st.secrets.get("PocketSignal")
    except Exception:
        return DEFAULT_API_PREDICT_URL

    if not pocketsignal:
        return DEFAULT_API_PREDICT_URL

    try:
        return str(pocketsignal.get("api_predict_url", DEFAULT_API_PREDICT_URL))
    except Exception:
        return DEFAULT_API_PREDICT_URL


API_PREDICT_URL = resolve_api_predict_url()


def load_demo_cases() -> dict[str, dict]:
    """Load exact demo cases generated from the current trained model bundle."""
    if not DEMO_CASES_PATH.exists():
        return {}
    try:
        data = json.loads(DEMO_CASES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data.get("demo_cases", {}) or {}


def load_metrics_snapshot() -> dict[str, str]:
    """Load the headline validation metrics shown in the hero section."""
    if not METRICS_PATH.exists():
        return {}
    try:
        payload = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    metrics = payload.get("metrics", {}) or {}
    return {
        "roc_auc": f"{float(metrics.get('roc_auc', 0.0)):.4f}",
        "pr_auc": f"{float(metrics.get('pr_auc', 0.0)):.4f}",
        "block_precision": f"{100.0 * float(metrics.get('precision_block', 0.0)):.1f}%",
        "approve_fraud_rate": f"{100.0 * float(metrics.get('approve_fraud_rate', 0.0)):.3f}%",
    }


def post_predict(payload: dict) -> dict:
    req = Request(
        API_PREDICT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=FRONTEND_HTTP_TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        preferred_language = payload.get("preferred_language")
        return {
            "status": "Flag",
            "risk_score": 75,
            "top_features": ["unusual amount pattern", "unusual device or browser context"],
            "explanation": (
                f"Backend unavailable ({exc.__class__.__name__}). "
                f"{fallback_flag_message(preferred_language, payload.get('TransactionAmt'))}"
            ),
            "latency_ms": 0.0,
            "model_version": "fallback",
        }


def status_badge(status: str) -> str:
    colors = {
        "Approve": ("#138f5a", "#f8fffb"),
        "Flag": ("#f5bd12", "#191200"),
        "Block": ("#d84834", "#fff7f5"),
    }
    color, text_color = colors.get(status, ("#475569", "#f8fafc"))
    return (
        "<span class='status-pill' "
        f"style='background:{color};color:{text_color};'>{escape(status)}</span>"
    )


def render_transaction_stream(rows: list[dict]) -> None:
    st.markdown("### Decision Board")
    if not rows:
        st.info("No transactions yet. Load an exact demo case to populate the board.")
        return

    html_rows = []
    for row in rows[:8]:
        html_rows.append(
            "<tr>"
            f"<td>{escape(str(row.get('TransactionID', 'n/a')))}</td>"
            f"<td>{float(row.get('TransactionAmt', 0.0)):.2f}</td>"
            f"<td>{status_badge(str(row.get('status', 'Flag')))}</td>"
            f"<td>{escape(str(row.get('risk_score', 'n/a')))}</td>"
            f"<td>{float(row.get('latency_ms', 0.0)):.1f}</td>"
            "</tr>"
        )

    html = (
        "<div class='table-wrap'>"
        "<table class='signal-table'>"
        "<thead><tr><th>TransactionID</th><th>Amount</th><th>Status</th><th>Risk</th><th>Latency (ms)</th></tr></thead>"
        f"<tbody>{''.join(html_rows)}</tbody></table></div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_phone(messages: list[dict], literacy_mode: bool, latest_status: str | None) -> None:
    st.markdown("### Customer Recovery")
    st.caption("This panel keeps the latest flagged conversation even if the newest decision becomes Approve or Block.")
    st.markdown("<div class='phone-shell'><div class='phone-header'>PocketSignal Assist</div>", unsafe_allow_html=True)

    if not messages:
        st.markdown(
            "<div class='phone-body'><div class='bubble bot'>No flagged conversations yet.</div></div>",
            unsafe_allow_html=True,
        )
    else:
        latest_flag = messages[-1]
        meta = (
            f"Latest flagged case: TransactionID {latest_flag.get('transaction_id', 'unknown')}, "
            f"risk {latest_flag.get('risk_score', 'n/a')}"
        )
        if latest_status and latest_status != "Flag":
            meta += " (left board may now show a different route)"
        bubbles = [f"<div class='chat-meta'>{escape(meta)}</div>"]
        for msg in messages[-4:]:
            text = str(msg.get("text", ""))
            if literacy_mode and len(text) > 150:
                text = text[:150] + "..."
            bubbles.append(f"<div class='bubble bot'>{escape(text)}</div>")
            bubbles.append("<div class='bubble user'>I will check now.</div>")
        st.markdown(f"<div class='phone-body'>{''.join(bubbles)}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def random_payload() -> dict:
    amt = round(random.uniform(8.0, 1600.0), 2)
    return {
        "TransactionID": int(time.time() * 1000) % 100000000,
        "TransactionDT": random.randint(1_000_000, 15_000_000),
        "TransactionAmt": amt,
        "ProductCD": random.choice(["W", "C", "H", "S", "R"]),
        "card1": random.choice([13926, 12695, 10409, 10616, 15066]),
        "DeviceInfo": random.choice(["SM-G960", "iOS Device", "Windows", "MacOS", None]),
        "P_emaildomain": random.choice(["gmail.com", "yahoo.com", "hotmail.com", None]),
        "DeviceType": random.choice(["mobile", "desktop", None]),
    }


def submit_payload(payload: dict) -> None:
    """Send one transaction to the backend and persist the visible demo state."""
    response = post_predict(payload)
    enriched = dict(payload)
    enriched.update(response)
    st.session_state.transactions.insert(0, enriched)
    st.session_state.last_response = enriched
    if response.get("status") == "Flag":
        # The recovery panel intentionally preserves the latest flagged conversation
        # so judges can keep reading it even after a later Approve or Block case.
        st.session_state.messages.append(
            {
                "text": response.get("explanation", ""),
                "transaction_id": enriched.get("TransactionID"),
                "risk_score": response.get("risk_score"),
            }
        )


def response_profile_value(selection: str) -> str:
    return "fast_route" if selection == "Faster wording" else "judge_demo"


def apply_theme() -> None:
    st.set_page_config(page_title="PocketSignal", layout="wide", initial_sidebar_state="collapsed")
    st.markdown(
        """
<style>
:root {
  --bg-1: #07131d;
  --bg-2: #081a23;
  --panel: rgba(9, 20, 28, 0.84);
  --line: rgba(244, 194, 96, 0.16);
  --copy: #f5efe5;
  --muted: #b8b4aa;
  --accent: #f4c260;
}

.stApp {
  background:
    radial-gradient(circle at 12% 18%, rgba(244, 194, 96, 0.07), transparent 28%),
    linear-gradient(135deg, var(--bg-1), var(--bg-2));
  color: var(--copy);
  font-family: "Avenir Next", "Trebuchet MS", sans-serif;
}

[data-testid="stSidebar"] {
  display: none;
}

.block-container {
  max-width: 1280px;
  padding-top: 2rem;
  padding-bottom: 2rem;
}

h1, h2, h3 {
  font-family: "Baskerville", "Palatino Linotype", serif;
}

.hero {
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: 28px 30px 22px 30px;
  background: linear-gradient(135deg, rgba(10, 23, 32, 0.97), rgba(4, 12, 19, 0.92));
  box-shadow: 0 22px 56px rgba(0, 0, 0, 0.3);
}

.eyebrow {
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 0.45rem;
}

.hero-title {
  margin: 0;
  font-size: 3rem;
  line-height: 1;
}

.hero-copy {
  margin: 0.8rem 0 0.9rem 0;
  max-width: 920px;
  color: var(--muted);
  font-size: 1rem;
}

.summary-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.summary-pill {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 8px 12px;
  background: rgba(255,255,255,0.03);
  font-size: 0.88rem;
  color: #efe7d6;
}

.route-line {
  margin-top: 10px;
  color: var(--muted);
  font-size: 0.9rem;
}

.status-pill {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.panel-card {
  border: 1px solid var(--line);
  border-radius: 22px;
  background: var(--panel);
  padding: 18px 20px;
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.2);
}

.decision-strip {
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  background: rgba(255,255,255,0.03);
  padding: 12px 14px;
  margin-bottom: 14px;
}

.reason-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.reason-chip {
  border-radius: 999px;
  padding: 6px 10px;
  background: rgba(15, 141, 111, 0.18);
  border: 1px solid rgba(15, 141, 111, 0.28);
  color: #d7fff4;
  font-size: 0.82rem;
}

.table-wrap {
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  overflow: hidden;
  background: rgba(255,255,255,0.02);
}

.signal-table {
  width: 100%;
  border-collapse: collapse;
}

.signal-table th,
.signal-table td {
  text-align: left;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 0.95rem;
}

.signal-table th {
  color: var(--muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: 0.72rem;
}

.phone-shell {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 24px;
  background: rgba(6, 14, 21, 0.94);
  box-shadow: 0 18px 40px rgba(0,0,0,0.32);
}

.phone-header {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  font-weight: 700;
  color: #f2e4c5;
}

.phone-body {
  min-height: 420px;
  padding: 14px;
}

.chat-meta {
  color: #94a3b8;
  font-size: 12px;
  margin-bottom: 10px;
}

.bubble {
  max-width: 88%;
  padding: 10px 12px;
  margin: 8px 0;
  border-radius: 16px;
  line-height: 1.45;
  font-size: 0.96rem;
}

.bubble.bot {
  background: #243041;
  color: #f8fafc;
}

.bubble.user {
  background: #0f8d6f;
  color: #ecfdf8;
  margin-left: auto;
}

div[data-testid="stButton"] > button {
  border-radius: 14px;
  border: 1px solid rgba(244, 194, 96, 0.2);
  background: rgba(255,255,255,0.03);
  color: #f6f1e8;
  font-weight: 600;
}

div[data-testid="stButton"] > button:hover {
  border-color: rgba(244, 194, 96, 0.48);
}

@media (max-width: 900px) {
  .hero-title {
    font-size: 2.35rem;
  }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    apply_theme()

    if "transactions" not in st.session_state:
        st.session_state.transactions = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_response" not in st.session_state:
        st.session_state.last_response = None

    demo_cases = load_demo_cases()
    metrics = load_metrics_snapshot()
    st.markdown(
        f"""
<div class='hero'>
  <div class='eyebrow'>Team Cache Me</div>
  <h1 class='hero-title'>PocketSignal</h1>
  <div class='hero-copy'>
    Privacy-first fraud triage for digital wallets serving unbanked and low-confidence users.
    Approve and Block stay on the fast path. Flag activates a local recovery message only when needed.
  </div>
  <div class='summary-strip'>
    <div class='summary-pill'>ROC-AUC: <strong>{escape(metrics.get('roc_auc', 'n/a'))}</strong></div>
    <div class='summary-pill'>Block precision: <strong>{escape(metrics.get('block_precision', 'n/a'))}</strong></div>
    <div class='summary-pill'>Approve fraud rate: <strong>{escape(metrics.get('approve_fraud_rate', 'n/a'))}</strong></div>
    <div class='summary-pill'>Local recovery: <strong>richer or faster wording</strong></div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.22, 0.95], gap="large")

    with left_col:
        st.markdown("### Demo Console")
        st.caption("Use exact saved cases during judging. Manual test is only for ad-hoc checks.")

        response_profile_label = st.radio(
            "Recovery message mode",
            options=["Richer wording", "Faster wording"],
            horizontal=True,
            help="Richer wording uses local Ollama text generation. Faster wording uses a deterministic local template for lower latency.",
        )
        message_language = st.selectbox(
            "Message language",
            options=["English", "Bahasa Melayu"],
        )
        literacy_mode = st.toggle("Low-literacy mode", value=True)

        case_cols = st.columns([1.25, 1])
        with case_cols[0]:
            exact_case = st.selectbox("Load exact case", options=["Approve", "Flag", "Block"])
        with case_cols[1]:
            st.markdown("")
            st.markdown("")
            if st.button("Clear history", use_container_width=True):
                st.session_state.transactions = []
                st.session_state.messages = []
                st.session_state.last_response = None

        if st.button("Run selected exact case", use_container_width=True):
            selected = demo_cases.get(exact_case, {})
            payload = dict(selected.get("payload") or {})
            if payload:
                payload["preferred_language"] = message_language
                payload["response_profile"] = response_profile_value(response_profile_label)
                submit_payload(payload)

        st.caption(
            "Recommended live order: Approve -> Flag -> Block. "
            f"Current Flag mode: {response_profile_label}."
        )

        with st.expander("Manual test", expanded=False):
            with st.form("txn_form"):
                transaction_amt = st.number_input("TransactionAmt", min_value=0.0, value=120.5)
                transaction_dt = st.number_input("TransactionDT", min_value=0, value=86400)
                card1 = st.number_input("card1", min_value=0, value=13926)
                device_info = st.text_input("DeviceInfo", value="SM-G960")
                p_emaildomain = st.text_input("P_emaildomain", value="gmail.com")
                device_type = st.selectbox("DeviceType", options=["mobile", "desktop", ""])
                submitted = st.form_submit_button("Submit manual /predict test", use_container_width=True)

            if submitted:
                payload = {
                    "TransactionID": int(time.time() * 1000) % 100000000,
                    "TransactionDT": int(transaction_dt),
                    "TransactionAmt": float(transaction_amt),
                    "ProductCD": "W",
                    "card1": int(card1),
                    "DeviceInfo": device_info or None,
                    "P_emaildomain": p_emaildomain or None,
                    "DeviceType": device_type or None,
                    "preferred_language": message_language,
                    "response_profile": response_profile_value(response_profile_label),
                }
                submit_payload(payload)

            if st.button("Simulate random transaction", use_container_width=True):
                payload = random_payload()
                payload["preferred_language"] = message_language
                payload["response_profile"] = response_profile_value(response_profile_label)
                submit_payload(payload)

        latest = st.session_state.last_response
        st.markdown("")
        st.markdown("### Decision")
        if latest is None:
            st.info("No decision yet. Load an exact case to begin the demo.")
        else:
            st.markdown(
                (
                    "<div class='decision-strip'>"
                    f"<strong>Latest:</strong> {status_badge(str(latest.get('status', 'Flag')))} "
                    f"&nbsp;&nbsp; Risk: <code>{escape(str(latest.get('risk_score', 'n/a')))}</code> "
                    f"&nbsp;&nbsp; Latency: <code>{escape(str(latest.get('latency_ms', 'n/a')))} ms</code>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            top_reasons = latest.get("top_features") or []
            if top_reasons:
                reason_markup = "".join(
                    f"<span class='reason-chip'>{escape(str(reason))}</span>"
                    for reason in top_reasons[:3]
                )
                st.markdown(f"<div class='reason-strip'>{reason_markup}</div>", unsafe_allow_html=True)
        render_transaction_stream(st.session_state.transactions)

    with right_col:
        latest_status = None
        if st.session_state.last_response is not None:
            latest_status = str(st.session_state.last_response.get("status"))

        render_phone(st.session_state.messages, literacy_mode=literacy_mode, latest_status=latest_status)


if __name__ == "__main__":
    main()
