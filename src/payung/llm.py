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


def localize_risk_reasons(top_features: Sequence[str], language: str | None) -> str:
    """Translate presentation-safe risk reasons into the target demo language."""
    normalized = normalize_language(language)
    labels = [str(feature or "").strip() for feature in top_features if str(feature or "").strip()]
    if not labels:
        return "transaction behavior" if normalized == "english" else "corak transaksi"
    if normalized != "bahasa_melayu":
        return ", ".join(labels)

    reason_map = {
        "unusual amount pattern": "corak jumlah yang luar biasa",
        "payment card pattern": "corak kad pembayaran yang luar biasa",
        "historical activity pattern": "corak aktiviti lepas yang luar biasa",
        "shared fraud network linkage": "hubungan rangkaian yang mencurigakan",
        "unusual transaction timing": "masa transaksi yang luar biasa",
        "unusual device or browser context": "peranti atau pelayar yang tidak biasa",
        "email identity mismatch": "padanan e-mel yang mencurigakan",
        "location or address anomaly": "lokasi atau alamat yang luar biasa",
        "timing or account age pattern": "masa atau umur akaun yang luar biasa",
        "identity consistency signal": "isyarat identiti yang tidak sepadan",
        "transaction consistency signal": "corak transaksi yang tidak konsisten",
        "identity verification context": "konteks pengesahan identiti",
        "transaction behavior signal": "corak transaksi",
    }
    localized = [reason_map.get(label, "corak transaksi") for label in labels]
    return ", ".join(localized)


def fallback_flag_message(
    language: str | None,
    transaction_amt: float | None = None,
    low_literacy: bool = False,
) -> str:
    """Return a deterministic local recovery message when richer generation is skipped or unavailable."""
    normalized = normalize_language(language)
    if normalized == "bahasa_melayu":
        if low_literacy:
            return "Kami nampak transaksi luar biasa. Adakah anda yang membuat transaksi ini? Balas YA atau TIDAK."
        transaction_text = "transaksi ini" if transaction_amt is None else f"transaksi RM{transaction_amt:.2f} ini"
        return (
            f"Kami mengesan aktiviti luar biasa pada {transaction_text}. "
            "Adakah anda yang membuat transaksi ini? Balas YA untuk sahkan atau TIDAK untuk sekat."
        )
    if low_literacy:
        return "We saw an unusual payment. Did you make it? Reply YES or NO."
    transaction_text = "this transaction" if transaction_amt is None else f"this RM{transaction_amt:.2f} transaction"
    return (
        f"We noticed unusual activity on {transaction_text}. "
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
        "here is a possible confirmation message:",
        "here's a possible confirmation message:",
        "here is a friendly confirmation message:",
        "here's a friendly confirmation message:",
        "here is a confirmation message:",
        "here's a confirmation message:",
        "possible message:",
        "possible confirmation message:",
        "friendly confirmation message:",
        "confirmation message:",
        "message:",
        "berikut adalah mesej:",
        "berikut adalah cadangan mesej:",
        "ini adalah mesej:",
        "cadangan mesej:",
        "mesej:",
    )
    lowered = text.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix):
            text = text[len(prefix):].strip()
            lowered = text.lower()
            break

    text = re.split(r"(?i)\b(?:translation|note|explanation|meaning)\s*:", text, maxsplit=1)[0].strip()
    text = re.split(r"(?i)\b(?:terjemahan|nota|penjelasan)\s*:", text, maxsplit=1)[0].strip()
    text = text.strip().strip('"').strip("'").strip()
    text = re.sub(r"^```[a-zA-Z0-9_-]*", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    text = re.sub(r"\s+", " ", text)
    # Force in-sentence "Anda" back to lowercase when the model ignores the prompt style.
    text = re.sub(r"(?<!^)(?<![.?!]\s)\bAnda\b", "anda", text)
    return text


def should_use_fallback_message(message: str, language: str | None) -> bool:
    """Reject richer output when it still contains meta text or wrong-language scaffolding."""
    text = str(message or "").strip()
    if not text:
        return True

    lowered = text.lower()
    meta_markers = (
        "translation:",
        "note:",
        "explanation:",
        "meaning:",
        "possible confirmation message",
        "friendly confirmation message",
        "here is a ",
        "here's a ",
        "ini adalah",
        "berikut adalah",
    )
    if any(marker in lowered for marker in meta_markers):
        return True

    normalized = normalize_language(language)
    if normalized == "bahasa_melayu":
        english_markers = (
            "hello",
            "did you",
            "reply yes",
            "reply no",
            "payment",
            "transaction of",
            "we noticed",
            "we want",
        )
        if any(marker in lowered for marker in english_markers):
            return True
        if "ya" not in lowered or "tidak" not in lowered:
            return True
        malay_markers = ("adakah", "transaksi", "balas", "anda", "sahkan", "sekat", "luar biasa", "kami")
        return not any(marker in lowered for marker in malay_markers)

    if lowered.startswith("you "):
        return True
    if "yes" not in lowered or "no" not in lowered:
        return True
    return False


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
        normalized = normalize_language(language)
        feature_text = localize_risk_reasons(top_features, normalized)
        if normalized == "bahasa_melayu":
            reading_level = "extremely simple" if low_literacy else "very simple"
            transaction_phrase_ms = (
                "transaksi ini"
                if transaction_amt is None
                else f"transaksi RM{transaction_amt:.2f} ini"
            )
            return (
                "You are a digital wallet security assistant for a Malaysian user. "
                f"A transaction of {amt_text} is flagged. "
                f"Risk reason: {feature_text}. "
                f"Write exactly 2 complete sentences in {reading_level} local Malaysian Bahasa Melayu (strictly NOT Bahasa Indonesia). "
                "Use a friendly but professional tone. "
                f"Sentence 1 must inform the user about unusual activity on {transaction_phrase_ms} and naturally mention the risk reason in Malay. "
                "Sentence 2 must ask if they made the transaction and strictly end with 'Balas YA untuk sahkan atau TIDAK untuk sekat.' "
                "Ensure the word 'anda' is lowercase unless it starts a sentence. "
                "Do not use the word 'Apakah'; use 'Adakah' instead. "
                "Avoid technical feature names. "
                "Do not include any English words, translation, explanation, note, label, quotation marks, or bullet points. "
                "Return ONLY the final 2-sentence Malay message."
            )
        transaction_phrase_en = (
            "this transaction"
            if transaction_amt is None
            else f"this RM{transaction_amt:.2f} transaction"
        )
        reading_level = "very simple" if low_literacy else "simple"
        return (
            "You are a digital wallet assistant. "
            f"A transaction of {amt_text} is flagged. "
            f"Risk reason: {feature_text}. "
            f"Write exactly 2 complete sentences in {reading_level} English. "
            "Use a friendly but professional tone. "
            f"Sentence 1 must inform the user about unusual activity on {transaction_phrase_en} and naturally mention the risk reason. "
            "Sentence 2 must ask if the user made the transaction and say 'Reply YES to confirm or NO to block it.' "
            "Avoid technical feature names. "
            "Do not include any introduction, label, quotation marks, translation, explanation, note, or bullet points. "
            "Return only the final message."
        )

    def explain_flag(
        self,
        transaction_amt: float | None,
        top_features: Sequence[str],
        language: str | None = None,
        low_literacy: bool = False,
    ) -> str:
        """Return a richer local message when available, otherwise fall back deterministically."""
        normalized = normalize_language(language)
        if low_literacy:
            return fallback_flag_message(
                language=language,
                transaction_amt=transaction_amt,
                low_literacy=low_literacy,
            )

        prompt = self.build_flag_prompt(
            transaction_amt=transaction_amt,
            top_features=top_features,
            language=language,
            low_literacy=low_literacy,
        )
        message = self.generate(prompt)
        if message:
            cleaned = clean_generated_message(message)
            if cleaned and not should_use_fallback_message(cleaned, normalized):
                return cleaned
        return fallback_flag_message(
            language=language,
            transaction_amt=transaction_amt,
            low_literacy=low_literacy,
        )
