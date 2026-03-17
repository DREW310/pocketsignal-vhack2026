"""Tests for the leakage-safe preprocessing and feature-store helpers."""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from payung.preprocess import (
    add_behavior_features,
    add_graph_features,
    add_time_features,
    apply_feature_store,
    build_feature_store,
)


class PreprocessTests(unittest.TestCase):
    def test_behavior_features_are_historical(self) -> None:
        df = pd.DataFrame(
            {
                "TransactionDT": [100, 200, 150],
                "card1": [1, 1, 2],
                "TransactionAmt": [10.0, 30.0, 50.0],
            }
        )
        out = add_behavior_features(df, key_col="card1", amount_col="TransactionAmt", time_col="TransactionDT")
        out = out.sort_values("TransactionDT").reset_index(drop=True)

        self.assertEqual(float(out.loc[0, "card1_txn_count_past"]), 0.0)
        self.assertTrue(np.isnan(out.loc[0, "card1_amt_mean_past"]))
        self.assertEqual(float(out.loc[2, "card1_txn_count_past"]), 1.0)
        self.assertEqual(float(out.loc[2, "card1_amt_mean_past"]), 10.0)

    def test_graph_features_and_store(self) -> None:
        df = pd.DataFrame(
            {
                "TransactionDT": [100, 200, 300],
                "card1": [1, 1, 2],
                "TransactionAmt": [10.0, 20.0, 30.0],
                "DeviceInfo": ["A", "B", "A"],
                "P_emaildomain": ["x.com", "x.com", None],
            }
        )

        out = add_time_features(df)
        out = add_behavior_features(out)
        out = add_graph_features(out, use_networkx=False)

        self.assertIn("card1_device_degree", out.columns)
        self.assertIn("card1_email_degree", out.columns)

        store = build_feature_store(out)
        single = pd.DataFrame(
            {
                "TransactionDT": [400],
                "card1": [1],
                "TransactionAmt": [99.0],
                "DeviceInfo": ["A"],
                "P_emaildomain": ["x.com"],
            }
        )
        inferred = apply_feature_store(single, store)
        self.assertIn("card1_txn_count_past", inferred.columns)
        self.assertGreaterEqual(float(inferred.loc[0, "card1_txn_count_past"]), 1.0)


if __name__ == "__main__":
    unittest.main()
