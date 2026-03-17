"""PocketSignal demo dashboard.

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
from urllib.error import HTTPError, URLError
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
    except HTTPError as exc:
        raise RuntimeError(f"Backend returned HTTP {exc.code}.") from exc
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Backend unavailable ({exc.__class__.__name__}). Check that FastAPI is running and reachable."
        ) from exc


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
            f"<td>{escape(str(row.get('recovery_state', 'Not needed')))}</td>"
            f"<td>{escape(str(row.get('risk_score', 'n/a')))}</td>"
            f"<td>{float(row.get('latency_ms', 0.0)):.1f}</td>"
            "</tr>"
        )

    html = (
        "<div class='table-wrap'>"
        "<table class='signal-table'>"
        "<thead><tr><th>TransactionID</th><th>Amount</th><th>Status</th><th>Recovery</th><th>Risk</th><th>Latency (ms)</th></tr></thead>"
        f"<tbody>{''.join(html_rows)}</tbody></table></div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def confirmation_copy(language: str, action: str, low_literacy: bool) -> tuple[str, str, str]:
    normalized = "bahasa_melayu" if language == "Bahasa Melayu" else "english"
    if action == "confirm":
        if normalized == "bahasa_melayu":
            return (
                "YA",
                "YA, ini transaksi saya.",
                "Disahkan oleh pengguna. Transaksi boleh diteruskan.",
            )
        return (
            "YES",
            "YES, this was my payment.",
            "Confirmed by user. The transaction can continue.",
        )

    if normalized == "bahasa_melayu":
        detail = "Sekat dan semak secara manual." if low_literacy else "Transaksi disekat dan dihantar untuk semakan manual."
        return (
            "TIDAK",
            "TIDAK, sekat transaksi ini.",
            detail,
        )
    detail = "Blocked and sent for manual review." if low_literacy else "Blocked after denial and escalated to manual review."
    return (
        "NO",
        "NO, block this payment.",
        detail,
    )


def sync_recovery_state(transaction_id: int | None, recovery_state: str) -> None:
    if transaction_id is None:
        return
    for row in st.session_state.transactions:
        if int(row.get("TransactionID", -1)) == int(transaction_id):
            row["recovery_state"] = recovery_state
            break

    latest = st.session_state.last_response
    if latest is not None and int(latest.get("TransactionID", -1)) == int(transaction_id):
        latest["recovery_state"] = recovery_state


def resolve_latest_recovery(action: str) -> None:
    if not st.session_state.recoveries:
        return

    latest = st.session_state.recoveries[-1]
    if latest.get("resolution_state") != "Pending user confirmation":
        return

    low_literacy = bool(latest.get("low_literacy", False))
    button_label, user_text, assistant_text = confirmation_copy(
        str(latest.get("language", "English")),
        action=action,
        low_literacy=low_literacy,
    )
    latest["messages"].append({"speaker": "user", "text": user_text})
    latest["messages"].append({"speaker": "assistant", "text": assistant_text})

    if action == "confirm":
        latest["resolution_state"] = "Confirmed by user"
    else:
        latest["resolution_state"] = "Blocked after denial; escalated to manual review"
    latest["resolution_button"] = button_label
    sync_recovery_state(latest.get("transaction_id"), latest["resolution_state"])


def render_phone(recoveries: list[dict], latest_status: str | None) -> None:
    st.markdown("### Customer Recovery")
    st.caption("Flagged transactions appear here with the latest confirmation message.")
    st.markdown("<div class='phone-shell'><div class='phone-header'>PocketSignal Assist</div>", unsafe_allow_html=True)

    if not recoveries:
        st.markdown(
            "<div class='phone-body'><div class='bubble bot'>No flagged payment yet.</div></div>",
            unsafe_allow_html=True,
        )
    else:
        latest_flag = recoveries[-1]
        meta = f"Flagged transaction {latest_flag.get('transaction_id', 'unknown')}"
        bubbles = [f"<div class='chat-meta'>{escape(meta)}</div>"]
        for msg in latest_flag.get("messages", [])[-6:]:
            speaker = str(msg.get("speaker", "assistant"))
            text = str(msg.get("text", ""))
            css_class = "user" if speaker == "user" else "bot"
            bubbles.append(f"<div class='bubble {css_class}'>{escape(text)}</div>")
        st.markdown(f"<div class='phone-body'>{''.join(bubbles)}</div>", unsafe_allow_html=True)
        if latest_flag.get("resolution_state") == "Pending user confirmation":
            confirm_label, _, _ = confirmation_copy(
                str(latest_flag.get("language", "English")),
                action="confirm",
                low_literacy=bool(latest_flag.get("low_literacy", False)),
            )
            deny_label, _, _ = confirmation_copy(
                str(latest_flag.get("language", "English")),
                action="deny",
                low_literacy=bool(latest_flag.get("low_literacy", False)),
            )
            action_cols = st.columns(2)
            with action_cols[0]:
                if st.button(confirm_label, use_container_width=True, key=f"confirm_{latest_flag.get('transaction_id')}"):
                    resolve_latest_recovery("confirm")
                    st.rerun()
            with action_cols[1]:
                if st.button(deny_label, use_container_width=True, key=f"deny_{latest_flag.get('transaction_id')}"):
                    resolve_latest_recovery("deny")
                    st.rerun()
            st.caption("Choose how the user responds to complete the recovery check.")
        else:
            st.success(str(latest_flag.get("resolution_state", "Resolved")))
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
    enriched["recovery_state"] = "Not needed"
    st.session_state.transactions.insert(0, enriched)
    st.session_state.last_response = enriched
    st.session_state.last_error = None
    if response.get("status") == "Flag":
        # The recovery panel intentionally preserves the latest flagged conversation
        # so judges can keep reading it even after a later Approve or Block case.
        enriched["recovery_state"] = "Pending user confirmation"
        st.session_state.recoveries.append(
            {
                "messages": [
                    {
                        "speaker": "assistant",
                        "text": response.get("explanation", ""),
                    }
                ],
                "transaction_id": enriched.get("TransactionID"),
                "risk_score": response.get("risk_score"),
                "language": payload.get("preferred_language", "English"),
                "low_literacy": bool(payload.get("low_literacy", False)),
                "resolution_state": "Pending user confirmation",
            }
        )


def response_profile_value(selection: str) -> str:
    return "fast_route" if selection == "Fast wording" else "judge_demo"


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
  --muted: #d4ccbf;
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
  font-family: "Avenir Next", "Segoe UI", "Helvetica Neue", sans-serif;
  font-weight: 700;
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
  color: #e7dfd0;
  font-size: 1rem;
  line-height: 1.55;
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
  font-size: 0.92rem;
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
  color: #c7d2dd;
  font-size: 13px;
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

label, [data-testid="stWidgetLabel"], [data-testid="stMarkdownContainer"] p,
div[data-testid="stCaptionContainer"] p, div[role="radiogroup"] label {
  color: #efe7d6 !important;
}

div[data-testid="stCaptionContainer"] p {
  color: var(--muted) !important;
}

div[data-testid="stMarkdownContainer"] p {
  line-height: 1.55;
}

div[data-baseweb="select"] input,
div[data-baseweb="select"] div {
  font-size: 1rem;
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
    if "recoveries" not in st.session_state:
        st.session_state.recoveries = []
    if "last_response" not in st.session_state:
        st.session_state.last_response = None
    if "last_error" not in st.session_state:
        st.session_state.last_error = None

    demo_cases = load_demo_cases()
    metrics = load_metrics_snapshot()
    st.markdown(
        f"""
<div class='hero'>
  <h1 class='hero-title'>PocketSignal</h1>
  <div class='hero-copy'>
    Privacy-first fraud triage for digital wallets serving unbanked and low-confidence users.
    Approve and Block stay on the fast path. Flag activates a local recovery message only when needed.
  </div>
  <div class='summary-strip'>
    <div class='summary-pill'>ROC-AUC: <strong>{escape(metrics.get('roc_auc', 'n/a'))}</strong></div>
    <div class='summary-pill'>Block precision: <strong>{escape(metrics.get('block_precision', 'n/a'))}</strong></div>
    <div class='summary-pill'>Approve fraud rate: <strong>{escape(metrics.get('approve_fraud_rate', 'n/a'))}</strong></div>
    <div class='summary-pill'>Local recovery: <strong>on-device confirmation</strong></div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.22, 0.95], gap="large")

    with left_col:
        st.markdown("### Demo Console")
        st.caption("Run a saved case to show each route clearly.")
        if st.session_state.last_error:
            st.error(st.session_state.last_error)

        response_profile_label = st.radio(
            "Message style",
            options=["Natural wording", "Fast wording"],
            horizontal=True,
            help="Natural wording uses local text generation when available. Fast wording uses a stable local template.",
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
                st.session_state.recoveries = []
                st.session_state.last_response = None
                st.session_state.last_error = None

        if st.button("Run selected exact case", use_container_width=True):
            selected = demo_cases.get(exact_case, {})
            payload = dict(selected.get("payload") or {})
            if payload:
                payload["preferred_language"] = message_language
                payload["response_profile"] = response_profile_value(response_profile_label)
                payload["low_literacy"] = literacy_mode
                try:
                    submit_payload(payload)
                except RuntimeError as exc:
                    st.session_state.last_error = str(exc)
                    st.rerun()

        with st.expander("Optional custom input", expanded=False):
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
                    "low_literacy": literacy_mode,
                }
                try:
                    submit_payload(payload)
                except RuntimeError as exc:
                    st.session_state.last_error = str(exc)
                    st.rerun()

            if st.button("Simulate random transaction", use_container_width=True):
                payload = random_payload()
                payload["preferred_language"] = message_language
                payload["response_profile"] = response_profile_value(response_profile_label)
                payload["low_literacy"] = literacy_mode
                try:
                    submit_payload(payload)
                except RuntimeError as exc:
                    st.session_state.last_error = str(exc)
                    st.rerun()

        latest = st.session_state.last_response
        st.markdown("")
        st.markdown("### Decision")
        if latest is None:
            st.info("No decision yet. Load an exact case to begin the demo.")
        else:
            recovery_state = latest.get("recovery_state")
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
            if recovery_state and recovery_state != "Not needed":
                st.caption(f"Recovery outcome: {recovery_state}")
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

        render_phone(st.session_state.recoveries, latest_status=latest_status)


if __name__ == "__main__":
    main()
