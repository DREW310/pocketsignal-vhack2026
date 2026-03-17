"""Regression tests for the exact PocketSignal demo cases."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from payung.inference import PayungPredictor


class DemoCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle_path = ROOT / "artifacts" / "model_bundle.pkl"
        cls.demo_cases_path = ROOT / "reports" / "demo_cases.json"
        cls.predictor = PayungPredictor.from_path(str(cls.bundle_path))
        payload = json.loads(cls.demo_cases_path.read_text(encoding="utf-8"))
        cls.demo_cases = payload["demo_cases"]

    def test_exact_demo_cases_keep_expected_routes(self) -> None:
        expected = {
            "Approve": "Approve",
            "Flag": "Flag",
            "Block": "Block",
        }
        for name, status in expected.items():
            payload = dict(self.demo_cases[name]["payload"])
            result = self.predictor.predict(payload, llm_client=None)
            self.assertEqual(result.status, status)

    def test_flag_case_supports_bahasa_melayu_fast_route(self) -> None:
        payload = dict(self.demo_cases["Flag"]["payload"])
        payload["preferred_language"] = "Bahasa Melayu"
        payload["response_profile"] = "fast_route"
        result = self.predictor.predict(payload, llm_client=None)
        self.assertEqual(result.status, "Flag")
        self.assertIn("Balas YA", result.explanation)

    def test_flag_case_supports_low_literacy_fast_route(self) -> None:
        payload = dict(self.demo_cases["Flag"]["payload"])
        payload["preferred_language"] = "English"
        payload["response_profile"] = "fast_route"
        payload["low_literacy"] = True
        result = self.predictor.predict(payload, llm_client=None)
        self.assertEqual(result.status, "Flag")
        self.assertEqual(
            result.explanation,
            "We saw an unusual payment. Did you make it? Reply YES or NO.",
        )

    def test_flag_case_supports_english_richer_route_without_llm(self) -> None:
        payload = dict(self.demo_cases["Flag"]["payload"])
        payload["preferred_language"] = "English"
        payload["response_profile"] = "judge_demo"
        result = self.predictor.predict(payload, llm_client=None)
        self.assertEqual(result.status, "Flag")
        self.assertIn("Reply YES", result.explanation)


if __name__ == "__main__":
    unittest.main()
