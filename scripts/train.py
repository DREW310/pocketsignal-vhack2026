#!/usr/bin/env python3
"""Train the PocketSignal model bundle and write judge-facing evidence files."""

from __future__ import annotations

import argparse
import json
import os
import random
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

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "src"))

from payung.modeling import save_bundle, train_pipeline
from payung.preprocess import (
    add_behavior_features,
    add_graph_features,
    add_time_features,
    build_feature_store,
    load_identity_for_transaction_ids,
    merge_transaction_identity,
    sample_csv,
)
from payung.reporting import write_json, write_metrics_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Payung fraud detection pipeline")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to YAML config")
    parser.add_argument("--sample-frac", type=float, default=None, help="Override sample fraction")
    parser.add_argument("--no-networkx", action="store_true", help="Disable networkx graph generation")
    parser.add_argument(
        "--safe-mode",
        action="store_true",
        help="Use sklearn fallback model for environments where OpenMP boosters are unavailable.",
    )
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def write_leakage_report(path: Path, merged_rows: int, processed_rows: int, has_target_in_features: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Leakage Check Report",
        "",
        f"Generated: {datetime.now(tz=timezone.utc).isoformat()}",
        "",
        f"- Rows after merge: {merged_rows}",
        f"- Rows after preprocessing: {processed_rows}",
        f"- Target column included in feature set: {has_target_in_features}",
        "",
        "## Notes",
        "- Time-based split is used to avoid future leakage into earlier transactions.",
        "- Historical card behavior features are based on past rows only (cumcount/cumsum pattern).",
        "- Graph degree features are computed without using labels.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    config_path = ROOT / args.config
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    seed = int(config.get("seed", 2026))
    set_seed(seed)

    data_cfg = config["data"]
    feature_cfg = config["features"]
    model_cfg = config["model"]
    if args.safe_mode:
        model_cfg = dict(model_cfg)
        model_cfg["use_lightgbm"] = False
        model_cfg["enable_catboost_ensemble"] = False
        model_cfg["calibrator_method"] = "identity"
    routing_cfg = config["routing"]
    artifacts_cfg = config["artifacts"]

    sample_frac = float(args.sample_frac if args.sample_frac is not None else data_cfg.get("sample_frac", 1.0))
    target_col = str(data_cfg.get("target_col", "isFraud"))
    id_col = str(data_cfg.get("id_col", "TransactionID"))
    time_col = str(data_cfg.get("time_col", "TransactionDT"))

    train_transaction_path = ROOT / str(data_cfg["train_transaction"])
    train_identity_path = ROOT / str(data_cfg["train_identity"])

    print(f"[train] loading transaction data from {train_transaction_path} (sample_frac={sample_frac})")
    transaction_df = sample_csv(str(train_transaction_path), frac=sample_frac, seed=seed)

    print(f"[train] loading matching identity rows from {train_identity_path}")
    identity_df = load_identity_for_transaction_ids(
        str(train_identity_path),
        transaction_ids=transaction_df[id_col].tolist(),
        id_col=id_col,
    )

    print("[train] merging transaction and identity")
    merged = merge_transaction_identity(transaction_df, identity_df, id_col=id_col)

    print("[train] feature engineering")
    processed = add_time_features(merged, time_col=time_col)
    processed = add_behavior_features(processed, key_col="card1", amount_col="TransactionAmt", time_col=time_col)
    processed = add_graph_features(
        processed,
        left_col="card1",
        graph_pairs=feature_cfg.get("graph", {}).get("pairs", []),
        use_networkx=bool(feature_cfg.get("graph", {}).get("use_networkx", True)) and not args.no_networkx,
    )

    print("[train] building feature store")
    feature_store = build_feature_store(processed)

    print("[train] training models")
    bundle, metrics = train_pipeline(
        frame=processed,
        target_col=target_col,
        id_col=id_col,
        time_col=time_col,
        categorical_candidates=feature_cfg.get("categorical", []),
        model_cfg=model_cfg,
        routing_cfg=routing_cfg,
        feature_store=feature_store,
    )

    model_bundle_path = ROOT / str(artifacts_cfg.get("model_bundle", "artifacts/model_bundle.pkl"))
    metrics_json_path = ROOT / str(artifacts_cfg.get("metrics_json", "reports/metrics.json"))
    metrics_md_path = ROOT / str(artifacts_cfg.get("metrics_md", "reports/metrics_report.md"))
    leakage_report_path = ROOT / "reports" / "leakage_check.md"

    model_bundle_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_json_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[train] saving bundle to {model_bundle_path}")
    save_bundle(bundle, str(model_bundle_path))

    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "config_path": str(config_path),
        "sample_frac": sample_frac,
        "rows": int(len(processed)),
        "metrics": metrics,
        "training_summary": bundle.get("training_summary", {}),
        "thresholds": bundle.get("thresholds", {}),
        "seed": seed,
    }
    write_json(payload, str(metrics_json_path))
    write_metrics_markdown(metrics, str(metrics_md_path))

    feature_columns = set(bundle.get("feature_columns", []))
    write_leakage_report(
        leakage_report_path,
        merged_rows=len(merged),
        processed_rows=len(processed),
        has_target_in_features=target_col in feature_columns,
    )

    print("[train] complete")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
