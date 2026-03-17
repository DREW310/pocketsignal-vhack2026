#!/usr/bin/env python3
"""Latency benchmarking helper for PocketSignal submission evidence."""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load test PocketSignal /predict endpoint")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:8000/predict")
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--output", type=str, default="reports/latency_report.md")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument(
        "--scenario",
        type=str,
        default="random",
        choices=["random", "approve", "flag", "block", "mixed_exact"],
        help="Traffic pattern for the latency run.",
    )
    parser.add_argument("--demo-cases", type=str, default="reports/demo_cases.json")
    parser.add_argument(
        "--response-profile",
        type=str,
        default="judge_demo",
        choices=["judge_demo", "fast_route"],
        help="Flag explanation mode. judge_demo uses richer local wording when available; fast_route uses deterministic local wording.",
    )
    return parser.parse_args()


def random_payload(idx: int) -> dict:
    return {
        "TransactionID": 9_000_000 + idx,
        "TransactionDT": random.randint(1_000_000, 15_000_000),
        "TransactionAmt": round(random.uniform(5.0, 3500.0), 2),
        "ProductCD": random.choice(["W", "C", "H", "S", "R"]),
        "card1": random.choice([13926, 12695, 15066, 10409, 10616]),
        "DeviceInfo": random.choice(["SM-G960", "iOS Device", "Windows", "MacOS", None]),
        "P_emaildomain": random.choice(["gmail.com", "yahoo.com", "hotmail.com", None]),
        "DeviceType": random.choice(["mobile", "desktop", None]),
        "response_profile": "judge_demo",
    }


def load_demo_cases(path: str) -> dict[str, dict]:
    demo_path = ROOT / path
    if not demo_path.exists():
        raise FileNotFoundError(f"Demo cases file not found: {demo_path}")
    data = json.loads(demo_path.read_text(encoding="utf-8"))
    return data.get("demo_cases", {}) or {}


def build_payloads(args: argparse.Namespace) -> list[dict]:
    if args.scenario == "random":
        payloads = [random_payload(i) for i in range(args.requests)]
        for payload in payloads:
            payload["response_profile"] = args.response_profile
        return payloads

    demo_cases = load_demo_cases(args.demo_cases)

    if args.scenario in {"approve", "flag", "block"}:
        key = args.scenario.capitalize()
        selected = dict((demo_cases.get(key) or {}).get("payload") or {})
        if not selected:
            raise ValueError(f"Missing exact demo case for scenario: {key}")
        payloads = []
        for idx in range(args.requests):
            payload = dict(selected)
            payload["TransactionID"] = int(selected.get("TransactionID", 0)) + idx + 1
            payload["response_profile"] = args.response_profile
            payloads.append(payload)
        return payloads

    mixed = []
    ordered = [
        dict((demo_cases.get("Approve") or {}).get("payload") or {}),
        dict((demo_cases.get("Flag") or {}).get("payload") or {}),
        dict((demo_cases.get("Block") or {}).get("payload") or {}),
    ]
    ordered = [payload for payload in ordered if payload]
    if not ordered:
        raise ValueError("No exact demo cases available for mixed_exact scenario.")

    for idx in range(args.requests):
        payload = dict(ordered[idx % len(ordered)])
        payload["TransactionID"] = int(payload.get("TransactionID", 0)) + idx + 1
        payload["response_profile"] = args.response_profile
        mixed.append(payload)
    return mixed


def request_once(url: str, payload: dict, timeout_seconds: float) -> dict:
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urlopen(req, timeout=timeout_seconds) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            total_ms = (time.perf_counter() - started) * 1000.0
            return {
                "ok": True,
                "status": body.get("status", "Unknown"),
                "roundtrip_ms": total_ms,
                "api_latency_ms": float(body.get("latency_ms", total_ms)),
            }
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        total_ms = (time.perf_counter() - started) * 1000.0
        return {"ok": False, "status": "Error", "roundtrip_ms": total_ms, "api_latency_ms": total_ms}


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    k = int(round((len(values) - 1) * q))
    return float(values[k])


def summarize(values: list[float]) -> dict:
    if not values:
        return {"count": 0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0}
    return {
        "count": len(values),
        "p50": percentile(values, 0.50),
        "p95": percentile(values, 0.95),
        "p99": percentile(values, 0.99),
        "avg": float(statistics.mean(values)),
    }


def write_report(path: str, result: dict) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Latency Report",
        "",
        f"Generated: {datetime.now(tz=timezone.utc).isoformat()}",
        "",
        "## Run Metadata",
        "",
        f"- Scenario: `{result['scenario']}`",
        f"- Response profile: `{result['response_profile']}`",
        f"- Timeout seconds: `{result['timeout_seconds']}`",
        f"- Error count: `{result['error_count']}`",
        "",
        "## Overall Roundtrip Latency (ms)",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Count | {result['overall']['count']} |",
        f"| Avg | {result['overall']['avg']:.3f} |",
        f"| p50 | {result['overall']['p50']:.3f} |",
        f"| p95 | {result['overall']['p95']:.3f} |",
        f"| p99 | {result['overall']['p99']:.3f} |",
        "",
        "## Per Route Roundtrip Latency (ms)",
        "",
        "| Status | Count | Avg | p50 | p95 | p99 |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for status, stats in result["by_status"].items():
        lines.append(
            f"| {status} | {stats['count']} | {stats['avg']:.3f} | {stats['p50']:.3f} | {stats['p95']:.3f} | {stats['p99']:.3f} |"
        )

    lines.extend([
        "",
        "## Gate C Check",
        "",
        f"- Approve/Block p95 < 50ms: {result['gate_c']['approve_block_ok']}",
        f"- Flag p95 < 1s: {result['gate_c']['flag_ok']}",
    ])

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    payloads = build_payloads(args)

    all_results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(request_once, args.url, payload, args.timeout) for payload in payloads]
        for future in as_completed(futures):
            all_results.append(future.result())

    roundtrip_all = [r["roundtrip_ms"] for r in all_results]
    by_status: dict[str, list[float]] = {}
    for row in all_results:
        by_status.setdefault(row["status"], []).append(row["roundtrip_ms"])

    summarized = {status: summarize(values) for status, values in by_status.items()}

    approve_p95 = summarized.get("Approve", {}).get("p95", 0.0)
    block_p95 = summarized.get("Block", {}).get("p95", 0.0)
    flag_p95 = summarized.get("Flag", {}).get("p95", 0.0)

    result = {
        "scenario": args.scenario,
        "response_profile": args.response_profile,
        "timeout_seconds": args.timeout,
        "error_count": int(sum(1 for row in all_results if not row["ok"])),
        "overall": summarize(roundtrip_all),
        "by_status": summarized,
        "gate_c": {
            "approve_block_ok": bool(max(approve_p95, block_p95) < 50.0) if ("Approve" in summarized or "Block" in summarized) else False,
            "flag_ok": bool(flag_p95 < 1000.0) if "Flag" in summarized else False,
        },
    }

    write_report(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
