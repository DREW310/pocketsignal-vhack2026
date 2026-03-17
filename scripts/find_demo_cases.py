#!/usr/bin/env python3
"""Create reproducible Approve / Flag / Block demo cases for judging."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "src"))

from payung.inference import PayungPredictor
from payung.preprocess import load_identity_for_transaction_ids, merge_transaction_identity, sample_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find demo-ready Approve / Flag / Block cases")
    parser.add_argument("--bundle", type=str, default="artifacts/model_bundle.pkl")
    parser.add_argument("--transaction-csv", type=str, default="test_transaction.csv")
    parser.add_argument("--identity-csv", type=str, default="test_identity.csv")
    parser.add_argument("--sample-frac", type=float, default=0.02)
    parser.add_argument("--output", type=str, default="reports/demo_cases.json")
    return parser.parse_args()


def normalize_payload(row: pd.Series) -> dict[str, Any]:
    """Convert one pandas row into JSON-safe API input."""
    payload: dict[str, Any] = {}
    for key, value in row.items():
        if pd.isna(value):
            continue
        if hasattr(value, "item"):
            payload[key] = value.item()
        else:
            payload[key] = value
    return payload


def main() -> None:
    args = parse_args()
    predictor = PayungPredictor.from_path(str(ROOT / args.bundle))

    transaction_df = sample_csv(str(ROOT / args.transaction_csv), frac=args.sample_frac, seed=2026)
    identity_df = load_identity_for_transaction_ids(
        str(ROOT / args.identity_csv),
        transaction_ids=transaction_df["TransactionID"].tolist(),
        id_col="TransactionID",
    )
    merged = merge_transaction_identity(transaction_df, identity_df, id_col="TransactionID")

    payloads = [normalize_payload(row) for _, row in merged.iterrows()]
    results = predictor.predict_batch(payloads)

    scored_rows: list[dict[str, Any]] = []
    for payload, result in zip(payloads, results):
        scored_rows.append(
            {
                "payload": payload,
                "status": result.status,
                "risk_score": result.risk_score,
                "probability": result.probability,
                "top_features": result.top_features,
                "explanation": result.explanation,
            }
        )

    thresholds = predictor.bundle.get("thresholds", {})
    approve_threshold = int(thresholds.get("approve_threshold", 70))
    block_threshold = int(thresholds.get("block_threshold", 90))
    flag_midpoint = (approve_threshold + block_threshold) / 2.0

    approve_cases = sorted(
        [row for row in scored_rows if row["status"] == "Approve"],
        key=lambda item: item["risk_score"],
    )
    flag_cases = sorted(
        [row for row in scored_rows if row["status"] == "Flag"],
        key=lambda item: abs(item["risk_score"] - flag_midpoint),
    )
    block_cases = sorted(
        [row for row in scored_rows if row["status"] == "Block"],
        key=lambda item: item["risk_score"],
        reverse=True,
    )

    output = {
        "thresholds": {
            "approve_threshold": approve_threshold,
            "block_threshold": block_threshold,
        },
        "counts": {
            "Approve": len(approve_cases),
            "Flag": len(flag_cases),
            "Block": len(block_cases),
        },
        "demo_cases": {
            "Approve": approve_cases[0] if approve_cases else None,
            "Flag": flag_cases[0] if flag_cases else None,
            "Block": block_cases[0] if block_cases else None,
        },
    }

    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
