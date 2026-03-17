"""Tests for the calibrated PocketSignal route boundaries."""

from __future__ import annotations

import unittest

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from payung.modeling import optimize_thresholds, route_status


class RoutingTests(unittest.TestCase):
    def test_routing_boundaries(self) -> None:
        approve = 70
        block = 90

        self.assertEqual(route_status(69, approve, block), "Approve")
        self.assertEqual(route_status(70, approve, block), "Flag")
        self.assertEqual(route_status(90, approve, block), "Flag")
        self.assertEqual(route_status(91, approve, block), "Block")

    def test_threshold_optimizer_can_limit_flag_share(self) -> None:
        risk = np.arange(0, 101)
        y_true = np.zeros_like(risk)
        y_true[risk >= 98] = 1

        optimized = optimize_thresholds(
            y_true=y_true,
            risk_score=risk,
            default_approve=65,
            default_block=98,
            target_block_fpr=0.05,
            target_approve_fraud_rate=0.05,
            min_approve_share=0.50,
            min_flag_share=0.10,
            min_block_share=0.01,
            max_flag_share=0.40,
            target_approve_share=0.60,
            target_flag_share=0.35,
            target_block_share=0.02,
        )

        approve_threshold = optimized["approve_threshold"]
        block_threshold = optimized["block_threshold"]
        self.assertGreaterEqual(approve_threshold, 50)
        self.assertLessEqual(block_threshold, 99)


if __name__ == "__main__":
    unittest.main()
