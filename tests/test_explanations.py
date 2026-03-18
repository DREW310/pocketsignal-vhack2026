"""Tests for explanation wording and response-profile normalization."""

from __future__ import annotations

import unittest

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from payung.inference import friendly_feature_reason, parse_low_literacy
from payung.llm import (
    clean_generated_message,
    fallback_flag_message,
    localize_risk_reasons,
    normalize_language,
    normalize_response_profile,
    OllamaClient,
    should_use_fallback_message,
)


class ExplanationTests(unittest.TestCase):
    def test_feature_reason_mapping_is_human_friendly(self) -> None:
        self.assertEqual(friendly_feature_reason("TransactionAmt"), "unusual amount pattern")
        self.assertEqual(friendly_feature_reason("card1"), "payment card pattern")
        self.assertEqual(friendly_feature_reason("C1"), "historical activity pattern")
        self.assertEqual(friendly_feature_reason("card1_device_degree"), "shared fraud network linkage")
        self.assertEqual(
            localize_risk_reasons(
                ["payment card pattern", "historical activity pattern", "unusual amount pattern"],
                "Bahasa Melayu",
            ),
            "corak kad pembayaran yang luar biasa, corak aktiviti lepas yang luar biasa, corak jumlah yang luar biasa",
        )

    def test_language_normalization_and_fallback(self) -> None:
        self.assertEqual(normalize_language("bm"), "bahasa_melayu")
        self.assertEqual(normalize_language("Bahasa Melayu"), "bahasa_melayu")
        self.assertEqual(normalize_language("English"), "english")
        self.assertEqual(normalize_response_profile("fast"), "fast_route")
        self.assertEqual(normalize_response_profile("template"), "fast_route")
        self.assertEqual(normalize_response_profile("judge_demo"), "judge_demo")
        self.assertIn("Balas YA", fallback_flag_message("bm", 39.0))
        self.assertIn("Reply YES", fallback_flag_message("english", 39.0))
        self.assertEqual(
            fallback_flag_message("english", 39.0, low_literacy=True),
            "We saw an unusual payment. Did you make it? Reply YES or NO.",
        )
        self.assertEqual(
            fallback_flag_message("Bahasa Melayu", 39.0, low_literacy=True),
            "Kami nampak transaksi luar biasa. Adakah anda yang membuat transaksi ini? Balas YA atau TIDAK.",
        )
        self.assertTrue(parse_low_literacy(True))
        self.assertTrue(parse_low_literacy("YES"))
        self.assertFalse(parse_low_literacy("no"))

    def test_generated_message_cleanup_removes_common_wrapper_text(self) -> None:
        raw = 'Here is a possible message:\n\n"Hey! We noticed a transaction for $100.00. Did you make it?"'
        self.assertEqual(
            clean_generated_message(raw),
            "Hey! We noticed a transaction for $100.00. Did you make it?",
        )
        wrapped = (
            'Here is a friendly confirmation message:\n'
            '"Hey! We noticed a recent transaction of $100.00. Did you make this purchase?"\n'
            'Translation: "..."'
        )
        self.assertEqual(
            clean_generated_message(wrapped),
            "Hey! We noticed a recent transaction of $100.00. Did you make this purchase?",
        )
        wrapped_bm = 'Berikut adalah mesej: "Adakah Anda yang membuat transaksi ini? Balas YA atau TIDAK."'
        self.assertEqual(
            clean_generated_message(wrapped_bm),
            "Adakah anda yang membuat transaksi ini? Balas YA atau TIDAK.",
        )

    def test_generated_message_falls_back_when_meta_or_wrong_language_leaks_in(self) -> None:
        self.assertTrue(
            should_use_fallback_message(
                'Assalamualaikum! Kami mahu memastikan transaksi ini. Translation: "..."',
                "Bahasa Melayu",
            )
        )
        self.assertTrue(
            should_use_fallback_message(
                "Kami mahu mengesahkan transaksi ini.",
                "Bahasa Melayu",
            )
        )
        self.assertTrue(
            should_use_fallback_message(
                "Here is a friendly confirmation message: Did you make this payment?",
                "English",
            )
        )
        self.assertFalse(
            should_use_fallback_message(
                "We noticed unusual activity linked to a new device. Was this you? Reply YES to confirm or NO to block it.",
                "English",
            )
        )

    def test_low_literacy_still_uses_curated_template(self) -> None:
        class DummyClient(OllamaClient):
            def __init__(self) -> None:
                super().__init__("http://127.0.0.1:11434", "llama3", timeout_seconds=0.1)

            def generate(self, prompt: str) -> str:
                return 'Here is a friendly confirmation message: "Hello! Did you make this payment?"'

        client = DummyClient()
        self.assertEqual(
            client.explain_flag(100.0, ["unusual amount pattern"], language="English", low_literacy=True),
            "We saw an unusual payment. Did you make it? Reply YES or NO.",
        )

    def test_bahasa_melayu_natural_wording_uses_clean_llm_output(self) -> None:
        class DummyClient(OllamaClient):
            def __init__(self) -> None:
                super().__init__("http://127.0.0.1:11434", "llama3", timeout_seconds=0.1)

            def generate(self, prompt: str) -> str:
                return (
                    'Berikut adalah mesej: '
                    '"Kami mengesan aktiviti luar biasa pada transaksi RM100.00 ini. '
                    'Adakah anda yang membuat transaksi ini? Balas YA untuk sahkan atau TIDAK untuk sekat."'
                )

        client = DummyClient()
        self.assertEqual(
            client.explain_flag(100.0, ["unusual amount pattern"], language="Bahasa Melayu", low_literacy=False),
            "Kami mengesan aktiviti luar biasa pada transaksi RM100.00 ini. Adakah anda yang membuat transaksi ini? Balas YA untuk sahkan atau TIDAK untuk sekat.",
        )


if __name__ == "__main__":
    unittest.main()
