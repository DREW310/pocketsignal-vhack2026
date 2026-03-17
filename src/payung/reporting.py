"""Reporting helpers for PocketSignal evidence artifacts."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence


def ensure_parent(path: str) -> None:
    """Create the parent directory for a report or artifact file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def write_json(data: Mapping[str, Any], path: str) -> None:
    """Write a UTF-8 JSON artifact used by the dashboard or evidence pack."""
    ensure_parent(path)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def write_metrics_markdown(metrics: Mapping[str, Any], path: str, title: str = "PocketSignal Metrics Report") -> None:
    """Render the core validation metrics into judge-readable markdown."""
    ensure_parent(path)
    thresholds = metrics.get("thresholds", {})
    confusion = metrics.get("confusion_matrix_block", {})
    routes = metrics.get("route_distribution", {})

    lines = [
        f"# {title}",
        "",
        f"Generated: {datetime.utcnow().isoformat()}Z",
        "",
        "## Core Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| ROC-AUC | {metrics.get('roc_auc', 0.0):.6f} |",
        f"| PR-AUC | {metrics.get('pr_auc', 0.0):.6f} |",
        f"| Brier Score | {metrics.get('brier', 0.0):.6f} |",
        f"| Precision@Block | {metrics.get('precision_block', 0.0):.6f} |",
        f"| Recall@Block | {metrics.get('recall_block', 0.0):.6f} |",
        f"| FPR@Block | {metrics.get('false_positive_rate_block', 0.0):.6f} |",
        f"| Fraud Rate in Approve Bucket | {metrics.get('approve_fraud_rate', 0.0):.6f} |",
        "",
        "## Routing Thresholds",
        "",
        "| Route | Threshold Rule |",
        "|---|---|",
        f"| Approve | score < {thresholds.get('approve_threshold', 'N/A')} |",
        f"| Flag | {thresholds.get('approve_threshold', 'N/A')} <= score <= {thresholds.get('block_threshold', 'N/A')} |",
        f"| Block | score > {thresholds.get('block_threshold', 'N/A')} |",
        "",
        "## Confusion Matrix (Block as Positive)",
        "",
        "| Cell | Count |",
        "|---|---:|",
        f"| TN | {confusion.get('tn', 0)} |",
        f"| FP | {confusion.get('fp', 0)} |",
        f"| FN | {confusion.get('fn', 0)} |",
        f"| TP | {confusion.get('tp', 0)} |",
        "",
        "## Route Distribution",
        "",
        "| Status | Count |",
        "|---|---:|",
        f"| Approve | {routes.get('Approve', 0)} |",
        f"| Flag | {routes.get('Flag', 0)} |",
        f"| Block | {routes.get('Block', 0)} |",
    ]

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def write_ablation_markdown(rows: Sequence[Mapping[str, Any]], path: str) -> None:
    """Render ablation rows into a compact markdown comparison table."""
    ensure_parent(path)
    lines = [
        "# PocketSignal Ablation Report",
        "",
        f"Generated: {datetime.utcnow().isoformat()}Z",
        "",
        "| Variant | PR-AUC | Recall@Block | FPR@Block | Notes |",
        "|---|---:|---:|---:|---|",
    ]

    if not rows:
        lines.append("| N/A | 0.000000 | 0.000000 | 0.000000 | No ablation run yet |")
    else:
        for row in rows:
            lines.append(
                "| {variant} | {pr_auc:.6f} | {recall_block:.6f} | {fpr_block:.6f} | {notes} |".format(
                    variant=row.get("variant", "unknown"),
                    pr_auc=float(row.get("pr_auc", 0.0)),
                    recall_block=float(row.get("recall_block", 0.0)),
                    fpr_block=float(row.get("fpr_block", 0.0)),
                    notes=row.get("notes", ""),
                )
            )

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
