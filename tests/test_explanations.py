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
    normalize_language,
    normalize_response_profile,
)


class ExplanationTests(unittest.TestCase):
    def test_feature_reason_mapping_is_human_friendly(self) -> None:
        self.assertEqual(friendly_feature_reason("TransactionAmt"), "unusual amount pattern")
        self.assertEqual(friendly_feature_reason("card1"), "payment card pattern")
        self.assertEqual(friendly_feature_reason("C1"), "historical activity pattern")
        self.assertEqual(friendly_feature_reason("card1_device_degree"), "shared fraud network linkage")

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
            "Kami nampak transaksi luar biasa. Adakah ini anda? Balas YA atau TIDAK.",
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


if __name__ == "__main__":
    unittest.main()
