"""Local wording helpers for PocketSignal.

This module keeps all recovery messaging local:
- deterministic fallback templates
- local Ollama richer wording generation
- language and response-profile normalization
"""

from __future__ import annotations

import json
import re
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


def fallback_flag_message(
    language: str | None,
    transaction_amt: float | None = None,
    low_literacy: bool = False,
) -> str:
    """Return a deterministic local recovery message when richer generation is skipped or unavailable."""
    normalized = normalize_language(language)
    if normalized == "bahasa_melayu":
        if low_literacy:
            return "Kami nampak transaksi luar biasa. Adakah ini anda? Balas YA atau TIDAK."
        amt_text = "transaksi ini" if transaction_amt is None else f"transaksi bernilai {transaction_amt:.2f}"
        return (
            f"Kami nampak aktiviti luar biasa pada {amt_text}. "
            "Adakah anda yang buat transaksi ini? Balas YA untuk sahkan atau TIDAK untuk sekat."
        )
    if low_literacy:
        return "We saw an unusual payment. Did you make it? Reply YES or NO."
    amt_text = "this payment" if transaction_amt is None else f"this payment of {transaction_amt:.2f}"
    return (
        f"We noticed unusual activity on {amt_text}. "
        "Did you make this transaction? Reply YES to confirm or NO to block it."
    )


def clean_generated_message(message: str) -> str:
    """Strip common LLM wrapper text so the UI shows only the user-facing message."""
    text = str(message or "").strip()
    if not text:
        return ""

    prefixes = (
        "here is a possible message:",
        "here's a possible message:",
        "here is a friendly message:",
        "here's a friendly message:",
        "possible message:",
        "message:",
    )
    lowered = text.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix):
            text = text[len(prefix):].strip()
            lowered = text.lower()
            break

    text = text.strip().strip('"').strip("'").strip()
    text = re.sub(r"^```[a-zA-Z0-9_-]*", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    text = re.sub(r"\s+", " ", text)
    return text


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
        low_literacy: bool = False,
    ) -> str:
        """Build the richer local wording prompt without exposing raw feature names to the user."""
        amt_text = "unknown amount" if transaction_amt is None else f"{transaction_amt:.2f}"
        feature_text = ", ".join(top_features) if top_features else "transaction behavior"
        normalized = normalize_language(language)
        if normalized == "bahasa_melayu":
            reading_level = "extremely simple" if low_literacy else "very simple"
            return (
                "You are a digital wallet assistant for a Malaysian or ASEAN wallet user. "
                f"A transaction of {amt_text} is flagged. "
                f"Human-readable risk reasons are {feature_text}. "
                f"Write a friendly, 2-sentence chat confirmation message in {reading_level} Bahasa Melayu. "
                "Ask whether the user made the transaction, avoid technical feature names, "
                "and use only short, clear wording that a lower-digital-literacy user can understand. "
                "Return only the message text, with no introduction, label, quotation marks, or bullet points."
            )
        reading_level = "very simple" if low_literacy else "simple"
        return (
            "You are a digital wallet assistant. "
            f"A transaction of {amt_text} is flagged. "
            f"Human-readable risk reasons are {feature_text}. "
            f"Write a friendly, 2-sentence chat confirmation message in {reading_level} English "
            "asking the wallet user if they made this transaction. Avoid technical feature names. "
            "Use short sentences and a direct YES or NO confirmation ask. "
            "Return only the message text, with no introduction, label, quotation marks, or bullet points."
        )

    def explain_flag(
        self,
        transaction_amt: float | None,
        top_features: Sequence[str],
        language: str | None = None,
        low_literacy: bool = False,
    ) -> str:
        """Return a richer local message when available, otherwise fall back deterministically."""
        prompt = self.build_flag_prompt(
            transaction_amt=transaction_amt,
            top_features=top_features,
            language=language,
            low_literacy=low_literacy,
        )
        message = self.generate(prompt)
        if message:
            cleaned = clean_generated_message(message)
            if cleaned:
                return cleaned
        return fallback_flag_message(
            language=language,
            transaction_amt=transaction_amt,
            low_literacy=low_literacy,
        )
