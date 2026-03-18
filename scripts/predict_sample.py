#!/usr/bin/env python3
"""Run one local PocketSignal prediction for quick smoke testing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "src"))

from payung.inference import PayungPredictor
from payung.llm import OllamaClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a single local prediction from model bundle")
    parser.add_argument("--bundle", type=str, default="artifacts/model_bundle.pkl")
    parser.add_argument("--llm", action="store_true", help="Enable local Ollama explanation for Flag cases")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    predictor = PayungPredictor.from_path(str(ROOT / args.bundle))

    llm_client = None
    if args.llm:
        llm_client = OllamaClient(base_url="http://127.0.0.1:11434", model="llama3", timeout_seconds=5.0)

    sample_payload = {
        "TransactionID": 99000001,
        "TransactionDT": 86400,
        "TransactionAmt": 899.75,
        "ProductCD": "W",
        "card1": 13926,
        "DeviceInfo": "SM-G960",
        "P_emaildomain": "gmail.com",
        "DeviceType": "mobile",
    }

    result = predictor.predict(sample_payload, llm_client=llm_client)
    print(
        json.dumps(
            {
                "status": result.status,
                "risk_score": result.risk_score,
                "probability": result.probability,
                "top_features": result.top_features,
                "explanation": result.explanation,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
