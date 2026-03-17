"""Tests for the calibrated PocketSignal route boundaries."""

from __future__ import annotations

import unittest

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from payung.modeling import route_status


class RoutingTests(unittest.TestCase):
    def test_routing_boundaries(self) -> None:
        approve = 70
        block = 90

        self.assertEqual(route_status(69, approve, block), "Approve")
        self.assertEqual(route_status(70, approve, block), "Flag")
        self.assertEqual(route_status(90, approve, block), "Flag")
        self.assertEqual(route_status(91, approve, block), "Block")


if __name__ == "__main__":
    unittest.main()
