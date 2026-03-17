"""Feature engineering utilities for PocketSignal.

These functions build the three main signal families used in the project:
- behavioral profiling
- time-derived features
- graph/context features
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Sequence

import networkx as nx
import numpy as np
import pandas as pd


DEFAULT_CHUNK_SIZE = 100_000


def sample_csv(path: str, frac: float = 1.0, seed: int = 2026, chunksize: int = DEFAULT_CHUNK_SIZE) -> pd.DataFrame:
    """Read a CSV with optional chunk-level sampling to keep memory bounded."""
    if frac <= 0:
        raise ValueError("frac must be > 0")
    if frac >= 1.0:
        return pd.read_csv(path)

    sampled_chunks: list[pd.DataFrame] = []
    for i, chunk in enumerate(pd.read_csv(path, chunksize=chunksize)):
        n_take = int(round(len(chunk) * frac))
        if n_take <= 0:
            continue
        if n_take >= len(chunk):
            sampled_chunks.append(chunk)
            continue
        sampled_chunks.append(chunk.sample(n=n_take, random_state=seed + i))

    if not sampled_chunks:
        return pd.read_csv(path, nrows=1)
    return pd.concat(sampled_chunks, ignore_index=True)


def load_identity_for_transaction_ids(
    identity_csv: str,
    transaction_ids: Iterable[Any],
    id_col: str = "TransactionID",
    chunksize: int = DEFAULT_CHUNK_SIZE,
) -> pd.DataFrame:
    """Read only identity rows that match the sampled transaction IDs."""
    id_set = set(transaction_ids)
    kept_chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(identity_csv, chunksize=chunksize):
        kept = chunk[chunk[id_col].isin(id_set)]
        if not kept.empty:
            kept_chunks.append(kept)

    if not kept_chunks:
        return pd.DataFrame(columns=[id_col])
    return pd.concat(kept_chunks, ignore_index=True)


def merge_transaction_identity(
    transaction_df: pd.DataFrame,
    identity_df: pd.DataFrame,
    id_col: str = "TransactionID",
) -> pd.DataFrame:
    """Preserve every transaction row and attach identity columns when available."""
    return transaction_df.merge(identity_df, on=id_col, how="left")


def add_time_features(df: pd.DataFrame, time_col: str = "TransactionDT") -> pd.DataFrame:
    frame = df.copy()
    if time_col not in frame.columns:
        frame[time_col] = np.nan
    frame["hour"] = (frame[time_col] // 3600) % 24
    frame["day"] = (frame[time_col] // (3600 * 24)) % 7
    return frame


def add_behavior_features(
    df: pd.DataFrame,
    key_col: str = "card1",
    amount_col: str = "TransactionAmt",
    time_col: str = "TransactionDT",
) -> pd.DataFrame:
    """Build leak-safe historical behavior features by sorting on transaction time first."""
    frame = df.sort_values(time_col, kind="mergesort").copy()

    if key_col not in frame.columns:
        frame["card1_txn_count_past"] = np.nan
        frame["card1_amt_mean_past"] = np.nan
        return frame

    grouped = frame.groupby(key_col, dropna=False)
    frame["card1_txn_count_past"] = grouped.cumcount().astype(float)

    if amount_col in frame.columns:
        cumsum = grouped[amount_col].cumsum() - frame[amount_col]
        denom = frame["card1_txn_count_past"].replace(0, np.nan)
        frame["card1_amt_mean_past"] = cumsum / denom
    else:
        frame["card1_amt_mean_past"] = np.nan

    return frame


def _to_key_series(series: pd.Series) -> pd.Series:
    return series.astype("string")


def _degree_map_groupby(frame: pd.DataFrame, left_col: str, right_col: str) -> Dict[str, float]:
    pairs = frame[[left_col, right_col]].dropna()
    if pairs.empty:
        return {}
    keyed = pairs.assign(_left_key=_to_key_series(pairs[left_col]))
    degree = keyed.groupby("_left_key", dropna=False)[right_col].nunique(dropna=True)
    return {str(k): float(v) for k, v in degree.dropna().to_dict().items()}


def _degree_map_networkx(frame: pd.DataFrame, left_col: str, right_col: str) -> Dict[str, float]:
    pairs = frame[[left_col, right_col]].dropna().drop_duplicates()
    if pairs.empty:
        return {}

    left_prefix = f"{left_col}::"
    right_prefix = f"{right_col}::"

    graph = nx.Graph()
    graph.add_edges_from(
        (
            f"{left_prefix}{left_value}",
            f"{right_prefix}{right_value}",
        )
        for left_value, right_value in pairs.itertuples(index=False)
    )

    out: Dict[str, float] = {}
    prefix_len = len(left_prefix)
    for node, degree in graph.degree():
        if node.startswith(left_prefix):
            out[node[prefix_len:]] = float(degree)
    return out


def add_graph_features(
    df: pd.DataFrame,
    left_col: str = "card1",
    graph_pairs: Sequence[Mapping[str, str]] | None = None,
    use_networkx: bool = True,
) -> pd.DataFrame:
    """Add heterogeneous graph degree features while preserving NaN for missing context fields."""
    frame = df.copy()
    pairs = graph_pairs or [
        {"right_col": "DeviceInfo", "feature_name": "card1_device_degree"},
        {"right_col": "P_emaildomain", "feature_name": "card1_email_degree"},
    ]

    if left_col not in frame.columns:
        for pair in pairs:
            frame[pair["feature_name"]] = np.nan
        return frame

    key_series = _to_key_series(frame[left_col])

    for pair in pairs:
        right_col = pair["right_col"]
        feature_name = pair["feature_name"]

        frame[feature_name] = np.nan
        if right_col not in frame.columns:
            continue

        if use_networkx:
            degree_map = _degree_map_networkx(frame, left_col=left_col, right_col=right_col)
        else:
            degree_map = _degree_map_groupby(frame, left_col=left_col, right_col=right_col)

        mask = frame[right_col].notna() & frame[left_col].notna()
        frame.loc[mask, feature_name] = key_series.loc[mask].map(degree_map)

    return frame


def build_feature_store(df: pd.DataFrame) -> Dict[str, Any]:
    """Build lookup tables used during real-time inference."""
    store: Dict[str, Any] = {
        "card1_txn_count": {},
        "card1_amt_mean": {},
        "card1_device_degree": {},
        "card1_email_degree": {},
        "defaults": {
            "card1_txn_count_past": 0.0,
            "card1_amt_mean_past": np.nan,
            "card1_device_degree": np.nan,
            "card1_email_degree": np.nan,
        },
    }

    if "card1" not in df.columns:
        return store

    keyed = df.copy()
    keyed["_card_key"] = _to_key_series(keyed["card1"])

    txn_count = keyed.groupby("_card_key", dropna=False).size().dropna()
    store["card1_txn_count"] = {str(k): float(v) for k, v in txn_count.to_dict().items()}

    if "TransactionAmt" in keyed.columns:
        amt_mean = keyed.groupby("_card_key", dropna=False)["TransactionAmt"].mean().dropna()
        store["card1_amt_mean"] = {str(k): float(v) for k, v in amt_mean.to_dict().items()}
        if not amt_mean.empty:
            store["defaults"]["card1_amt_mean_past"] = float(amt_mean.median())

    if "card1_device_degree" in keyed.columns:
        device_degree = keyed.groupby("_card_key", dropna=False)["card1_device_degree"].mean().dropna()
        store["card1_device_degree"] = {str(k): float(v) for k, v in device_degree.to_dict().items()}
        if not device_degree.empty:
            store["defaults"]["card1_device_degree"] = float(device_degree.median())

    if "card1_email_degree" in keyed.columns:
        email_degree = keyed.groupby("_card_key", dropna=False)["card1_email_degree"].mean().dropna()
        store["card1_email_degree"] = {str(k): float(v) for k, v in email_degree.to_dict().items()}
        if not email_degree.empty:
            store["defaults"]["card1_email_degree"] = float(email_degree.median())

    return store


def apply_feature_store(df: pd.DataFrame, store: Mapping[str, Any]) -> pd.DataFrame:
    """Approximate historical and graph-aware features at inference time."""
    frame = add_time_features(df)

    if "card1" not in frame.columns:
        frame["card1_txn_count_past"] = np.nan
        frame["card1_amt_mean_past"] = np.nan
        frame["card1_device_degree"] = np.nan
        frame["card1_email_degree"] = np.nan
        return frame

    defaults = store.get("defaults", {})
    key_series = _to_key_series(frame["card1"])

    frame["card1_txn_count_past"] = key_series.map(store.get("card1_txn_count", {})).fillna(
        defaults.get("card1_txn_count_past", 0.0)
    )
    frame["card1_amt_mean_past"] = key_series.map(store.get("card1_amt_mean", {})).fillna(
        defaults.get("card1_amt_mean_past", np.nan)
    )

    frame["card1_device_degree"] = np.nan
    if "DeviceInfo" in frame.columns:
        mask_device = frame["DeviceInfo"].notna() & frame["card1"].notna()
        frame.loc[mask_device, "card1_device_degree"] = key_series.loc[mask_device].map(
            store.get("card1_device_degree", {})
        )

    frame["card1_email_degree"] = np.nan
    if "P_emaildomain" in frame.columns:
        mask_email = frame["P_emaildomain"].notna() & frame["card1"].notna()
        frame.loc[mask_email, "card1_email_degree"] = key_series.loc[mask_email].map(
            store.get("card1_email_degree", {})
        )

    frame["card1_device_degree"] = frame["card1_device_degree"].fillna(
        defaults.get("card1_device_degree", np.nan)
    )
    frame["card1_email_degree"] = frame["card1_email_degree"].fillna(
        defaults.get("card1_email_degree", np.nan)
    )

    return frame


def ensure_columns(df: pd.DataFrame, required_columns: Sequence[str]) -> pd.DataFrame:
    frame = df.copy()
    missing = [col for col in required_columns if col not in frame.columns]
    if missing:
        filler = pd.DataFrame(np.nan, index=frame.index, columns=missing)
        frame = pd.concat([frame, filler], axis=1)
    return frame
