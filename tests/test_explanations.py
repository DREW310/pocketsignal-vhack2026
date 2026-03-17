"""Tests for explanation wording and response-profile normalization."""

from __future__ import annotations

import unittest

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from payung.inference import friendly_feature_reason
from payung.llm import fallback_flag_message, normalize_language, normalize_response_profile


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


if __name__ == "__main__":
    unittest.main()
