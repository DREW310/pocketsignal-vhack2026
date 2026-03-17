#!/usr/bin/env python3
"""Preprocess IEEE-CIS data into PocketSignal feature-ready samples and reports."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

# Avoid OpenMP SHM issues on constrained environments.
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["KMP_AFFINITY"] = "disabled"
os.environ["KMP_INIT_AT_FORK"] = "FALSE"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import yaml

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "src"))

from payung.preprocess import (
    add_behavior_features,
    add_graph_features,
    add_time_features,
    load_identity_for_transaction_ids,
    merge_transaction_identity,
    sample_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess IEEE-CIS data for PocketSignal")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--sample-frac", type=float, default=None)
    parser.add_argument("--output-csv", type=str, default="artifacts/processed_sample.csv")
    parser.add_argument("--profile-md", type=str, default="reports/data_profile.md")
    parser.add_argument("--no-networkx", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = yaml.safe_load((ROOT / args.config).read_text(encoding="utf-8"))

    data_cfg = config["data"]
    feature_cfg = config["features"]
    seed = int(config.get("seed", 2026))

    sample_frac = float(args.sample_frac if args.sample_frac is not None else data_cfg.get("sample_frac", 0.1))
    id_col = data_cfg.get("id_col", "TransactionID")
    time_col = data_cfg.get("time_col", "TransactionDT")

    transaction_df = sample_csv(str(ROOT / data_cfg["train_transaction"]), frac=sample_frac, seed=seed)
    identity_df = load_identity_for_transaction_ids(
        str(ROOT / data_cfg["train_identity"]),
        transaction_ids=transaction_df[id_col].tolist(),
        id_col=id_col,
    )

    frame = merge_transaction_identity(transaction_df, identity_df, id_col=id_col)
    frame = add_time_features(frame, time_col=time_col)
    frame = add_behavior_features(frame, key_col="card1", amount_col="TransactionAmt", time_col=time_col)
    frame = add_graph_features(
        frame,
        left_col="card1",
        graph_pairs=feature_cfg.get("graph", {}).get("pairs", []),
        use_networkx=bool(feature_cfg.get("graph", {}).get("use_networkx", True)) and not args.no_networkx,
    )

    output_csv = ROOT / args.output_csv
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_csv, index=False)

    profile_path = ROOT / args.profile_md
    profile_path.parent.mkdir(parents=True, exist_ok=True)

    missing_device = float(frame["DeviceInfo"].isna().mean()) if "DeviceInfo" in frame.columns else 1.0
    missing_email = float(frame["P_emaildomain"].isna().mean()) if "P_emaildomain" in frame.columns else 1.0
    fraud_rate = float(frame[data_cfg.get("target_col", "isFraud")].mean()) if data_cfg.get("target_col", "isFraud") in frame.columns else 0.0

    lines = [
        "# Data Profile Report",
        "",
        f"Generated: {datetime.now(tz=timezone.utc).isoformat()}",
        "",
        f"- Sample fraction: {sample_frac}",
        f"- Rows after merge: {len(frame)}",
        f"- Fraud rate: {fraud_rate:.6f}",
        f"- DeviceInfo missing ratio: {missing_device:.6f}",
        f"- P_emaildomain missing ratio: {missing_email:.6f}",
        "",
        "## Engineered Features",
        "- hour",
        "- day",
        "- card1_txn_count_past",
        "- card1_amt_mean_past",
        "- card1_device_degree",
        "- card1_email_degree",
        "",
        "## Leakage Notes",
        "- Behavioral features use only historical rows after sorting by TransactionDT.",
        "- Graph features are label-agnostic and rely only on transactional context.",
    ]
    profile_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"saved {output_csv}")
    print(f"saved {profile_path}")


if __name__ == "__main__":
    main()
