#!/usr/bin/env python3
"""Run the PocketSignal ablation study used in the technical evidence deck."""

from __future__ import annotations

import argparse
import copy
import json
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

from payung.modeling import train_pipeline
from payung.preprocess import (
    add_behavior_features,
    add_graph_features,
    add_time_features,
    build_feature_store,
    load_identity_for_transaction_ids,
    merge_transaction_identity,
    sample_csv,
)
from payung.reporting import write_ablation_markdown, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ablation study for PocketSignal")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--sample-frac", type=float, default=0.05)
    parser.add_argument(
        "--safe-mode",
        action="store_true",
        help="Disable OpenMP boosters (LightGBM/CatBoost) and use sklearn fallback model.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = ROOT / args.config
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    data_cfg = config["data"]
    feature_cfg = config["features"]
    base_model_cfg = config["model"]
    if args.safe_mode:
        base_model_cfg = dict(base_model_cfg)
        base_model_cfg["use_lightgbm"] = False
        base_model_cfg["enable_catboost_ensemble"] = False
        base_model_cfg["calibrator_method"] = "identity"
    routing_cfg = config["routing"]
    artifacts_cfg = config["artifacts"]

    id_col = data_cfg.get("id_col", "TransactionID")
    target_col = data_cfg.get("target_col", "isFraud")
    time_col = data_cfg.get("time_col", "TransactionDT")

    transaction_df = sample_csv(str(ROOT / data_cfg["train_transaction"]), frac=args.sample_frac, seed=int(config.get("seed", 2026)))
    identity_df = load_identity_for_transaction_ids(
        str(ROOT / data_cfg["train_identity"]),
        transaction_ids=transaction_df[id_col].tolist(),
        id_col=id_col,
    )

    merged = merge_transaction_identity(transaction_df, identity_df, id_col=id_col)
    base = add_time_features(merged, time_col=time_col)
    base = add_behavior_features(base, key_col="card1", amount_col="TransactionAmt", time_col=time_col)

    with_graph = add_graph_features(
        base,
        left_col="card1",
        graph_pairs=feature_cfg.get("graph", {}).get("pairs", []),
        use_networkx=bool(feature_cfg.get("graph", {}).get("use_networkx", True)),
    )

    no_graph = base.copy()
    for pair in feature_cfg.get("graph", {}).get("pairs", []):
        feature_name = pair.get("feature_name")
        if feature_name:
            no_graph[feature_name] = float("nan")

    variants = [
        {
            "name": "baseline_no_graph_no_balance",
            "frame": no_graph,
            "model_cfg": {**copy.deepcopy(base_model_cfg), "class_weight_mode": "none", "enable_catboost_ensemble": False},
            "notes": "No graph features, no imbalance handling, no ensemble.",
        },
        {
            "name": "plus_imbalance_no_graph",
            "frame": no_graph,
            "model_cfg": {**copy.deepcopy(base_model_cfg), "class_weight_mode": "scale_pos_weight", "enable_catboost_ensemble": False},
            "notes": "Added class imbalance handling only.",
        },
        {
            "name": "full_graph_plus_ensemble",
            "frame": with_graph,
            "model_cfg": copy.deepcopy(base_model_cfg),
            "notes": "Graph features + imbalance + optional ensemble.",
        },
    ]

    rows = []
    full_output = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "sample_frac": args.sample_frac,
        "variants": [],
    }

    for variant in variants:
        frame = variant["frame"]
        feature_store = build_feature_store(frame)
        bundle, metrics = train_pipeline(
            frame=frame,
            target_col=target_col,
            id_col=id_col,
            time_col=time_col,
            categorical_candidates=feature_cfg.get("categorical", []),
            model_cfg=variant["model_cfg"],
            routing_cfg=routing_cfg,
            feature_store=feature_store,
        )
        _ = bundle

        rows.append(
            {
                "variant": variant["name"],
                "pr_auc": metrics.get("pr_auc", 0.0),
                "recall_block": metrics.get("recall_block", 0.0),
                "fpr_block": metrics.get("false_positive_rate_block", 0.0),
                "notes": variant["notes"],
            }
        )
        full_output["variants"].append({"name": variant["name"], "metrics": metrics, "notes": variant["notes"]})

    ablation_md = ROOT / str(artifacts_cfg.get("ablation_md", "reports/ablation_report.md"))
    ablation_json = ROOT / "reports" / "ablation_report.json"

    write_ablation_markdown(rows, str(ablation_md))
    write_json(full_output, str(ablation_json))
    print(json.dumps(full_output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
