"""Local wording helpers for PocketSignal.

This module keeps all recovery messaging local:
- deterministic fallback templates
- local Ollama richer wording generation
- language and response-profile normalization
"""

from __future__ import annotations

import json
from typing import Sequence
from urllib.error import URLError
from urllib.request import Request, urlopen


def normalize_language(language: str | None) -> str:
    """Normalize external language labels into the internal two-language set."""
    value = str(language or "english").strip().lower()
    if value in {"bm", "ms", "bahasa", "bahasa melayu", "bahasa_melayu", "malay", "melayu"}:
        return "bahasa_melayu"
    return "english"


def normalize_response_profile(profile: str | None) -> str:
    """Map UI or API wording mode labels into the internal routing profile."""
    value = str(profile or "judge_demo").strip().lower()
    if value in {"fast", "fast_route", "speed", "speed_mode", "template"}:
        return "fast_route"
    return "judge_demo"


def fallback_flag_message(language: str | None, transaction_amt: float | None = None) -> str:
    """Return a deterministic local recovery message when richer generation is skipped or unavailable."""
    normalized = normalize_language(language)
    if normalized == "bahasa_melayu":
        amt_text = "transaksi ini" if transaction_amt is None else f"transaksi bernilai {transaction_amt:.2f}"
        return (
            f"Kami nampak aktiviti luar biasa pada {amt_text}. "
            "Adakah anda yang buat transaksi ini? Balas YA untuk sahkan atau TIDAK untuk sekat."
        )
    amt_text = "this payment" if transaction_amt is None else f"this payment of {transaction_amt:.2f}"
    return (
        f"We noticed unusual activity on {amt_text}. "
        "Did you make this transaction? Reply YES to confirm or NO to block it."
    )


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float = 1.0,
        keep_alive: str = "10m",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.keep_alive = keep_alive

    def generate(self, prompt: str) -> str:
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": self.keep_alive,
        }
        req = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return str(data.get("response", "")).strip()
        except (URLError, TimeoutError, json.JSONDecodeError, OSError):
            return ""

    def preload(self) -> bool:
        """Warm the local model so repeated demo calls avoid a cold start when possible."""
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": "",
            "stream": False,
            "keep_alive": self.keep_alive,
        }
        req = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout_seconds) as resp:
                json.loads(resp.read().decode("utf-8"))
                return True
        except (URLError, TimeoutError, json.JSONDecodeError, OSError):
            return False

    def is_ready(self) -> bool:
        endpoint = f"{self.base_url}/api/tags"
        req = Request(endpoint, method="GET")
        try:
            with urlopen(req, timeout=self.timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError, OSError):
            return False

        models = data.get("models", [])
        expected = {self.model, f"{self.model}:latest"}
        for entry in models:
            name = str(entry.get("name") or entry.get("model") or "").strip()
            if name in expected:
                return True
        return False

    def build_flag_prompt(
        self,
        transaction_amt: float | None,
        top_features: Sequence[str],
        language: str | None = None,
    ) -> str:
        """Build the richer local wording prompt without exposing raw feature names to the user."""
        amt_text = "unknown amount" if transaction_amt is None else f"{transaction_amt:.2f}"
        feature_text = ", ".join(top_features) if top_features else "transaction behavior"
        normalized = normalize_language(language)
        if normalized == "bahasa_melayu":
            return (
                "You are a digital wallet assistant for a Malaysian or ASEAN wallet user. "
                f"A transaction of {amt_text} is flagged. "
                f"Human-readable risk reasons are {feature_text}. "
                "Write a friendly, 2-sentence chat confirmation message in very simple Bahasa Melayu. "
                "Ask whether the user made the transaction, avoid technical feature names, "
                "and keep the wording suitable for lower digital literacy users."
            )
        return (
            "You are a digital wallet assistant. "
            f"A transaction of {amt_text} is flagged. "
            f"Human-readable risk reasons are {feature_text}. "
            "Write a friendly, 2-sentence chat confirmation message in simple English "
            "asking the wallet user if they made this transaction. "
            "Avoid technical feature names."
        )

    def explain_flag(
        self,
        transaction_amt: float | None,
        top_features: Sequence[str],
        language: str | None = None,
    ) -> str:
        """Return a richer local message when available, otherwise fall back deterministically."""
        prompt = self.build_flag_prompt(
            transaction_amt=transaction_amt,
            top_features=top_features,
            language=language,
        )
        message = self.generate(prompt)
        if message:
            return message
        return fallback_flag_message(language=language, transaction_amt=transaction_amt)
