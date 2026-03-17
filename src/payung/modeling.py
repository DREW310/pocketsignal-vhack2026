"""Training, calibration, and routing utilities for PocketSignal.

The goal of this module is not just classification accuracy.
It produces a deployable bundle with calibrated scores and route thresholds
that support the PocketSignal triage workflow.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Sequence

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OrdinalEncoder

@dataclass
class IdentityCalibrator:
    """Fallback calibrator when a calibrator cannot be trained."""

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x).reshape(-1, 1)
        clipped = np.clip(x, 0.0, 1.0)
        return np.hstack([1.0 - clipped, clipped])


def _to_string_frame(x: Any) -> Any:
    return x.astype(str)


def split_train_calib_valid(
    df: pd.DataFrame,
    time_col: str,
    valid_frac: float,
    calib_frac: float,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ordered = df.sort_values(time_col, kind="mergesort").reset_index(drop=True)
    n_rows = len(ordered)
    n_valid = max(1, int(round(n_rows * valid_frac)))
    n_calib = max(1, int(round(n_rows * calib_frac)))

    if n_valid + n_calib >= n_rows:
        n_valid = max(1, n_rows // 5)
        n_calib = max(1, n_rows // 10)

    train_end = n_rows - n_valid - n_calib
    calib_end = n_rows - n_valid

    train_df = ordered.iloc[:train_end].copy()
    calib_df = ordered.iloc[train_end:calib_end].copy()
    valid_df = ordered.iloc[calib_end:].copy()
    return train_df, calib_df, valid_df


def select_feature_columns(
    df: pd.DataFrame,
    target_col: str,
    id_col: str,
) -> list[str]:
    excluded = {target_col, id_col}
    return [col for col in df.columns if col not in excluded]


def infer_column_types(
    df: pd.DataFrame,
    feature_columns: Sequence[str],
    categorical_candidates: Sequence[str],
) -> tuple[list[str], list[str]]:
    categorical = [col for col in categorical_candidates if col in feature_columns]
    for col in feature_columns:
        if col in categorical:
            continue
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            categorical.append(col)

    categorical = sorted(set(categorical))
    numeric = [col for col in feature_columns if col not in categorical]
    return numeric, categorical


def build_preprocessor(
    numeric_columns: Sequence[str],
    categorical_columns: Sequence[str],
) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="constant",
                    fill_value=-999.0,
                    keep_empty_features=True,
                ),
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="constant",
                    fill_value="missing",
                    keep_empty_features=True,
                ),
            ),
            ("to_string", FunctionTransformer(_to_string_frame, validate=False)),
            (
                "encoder",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                    encoded_missing_value=-2,
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, list(numeric_columns)),
            ("categorical", categorical_pipeline, list(categorical_columns)),
        ],
        sparse_threshold=0.0,
        remainder="drop",
    )
    return preprocessor


def _scale_pos_weight(y: np.ndarray) -> float:
    pos = float(np.sum(y == 1))
    neg = float(np.sum(y == 0))
    if pos <= 0:
        return 1.0
    return max(1.0, neg / pos)


def _train_lightgbm(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_eval: np.ndarray,
    y_eval: np.ndarray,
    params: Mapping[str, Any],
    class_weight_mode: str,
) -> Any:
    try:
        from lightgbm import LGBMClassifier
    except (ImportError, OSError) as exc:
        raise RuntimeError(
            "LightGBM failed to load. On macOS this usually means libomp is missing. "
            "Install it with `brew install libomp` and rerun training, or use "
            "`python3 scripts/train.py --sample-frac 0.10 --safe-mode` to unblock "
            "with the fallback model."
        ) from exc

    scale_weight = _scale_pos_weight(y_train)

    model = LGBMClassifier(
        objective="binary",
        n_estimators=int(params.get("n_estimators", 500)),
        learning_rate=float(params.get("learning_rate", 0.05)),
        num_leaves=int(params.get("num_leaves", 64)),
        subsample=float(params.get("subsample", 0.8)),
        colsample_bytree=float(params.get("colsample_bytree", 0.8)),
        reg_alpha=float(params.get("reg_alpha", 0.0)),
        reg_lambda=float(params.get("reg_lambda", 0.0)),
        random_state=int(params.get("random_state", 2026)),
        class_weight="balanced" if class_weight_mode == "balanced" else None,
        scale_pos_weight=scale_weight if class_weight_mode == "scale_pos_weight" else 1.0,
        n_jobs=-1,
    )

    model.fit(x_train, y_train, eval_set=[(x_eval, y_eval)], eval_metric="average_precision")
    return model


def _train_logistic_fallback(
    x_train: np.ndarray,
    y_train: np.ndarray,
    params: Mapping[str, Any],
    class_weight_mode: str,
) -> LogisticRegression:
    """Safe fallback model when OpenMP-backed boosters are unavailable."""
    scale_weight = _scale_pos_weight(y_train)
    sample_weight = None
    if class_weight_mode in {"scale_pos_weight", "balanced"}:
        sample_weight = np.where(y_train == 1, scale_weight, 1.0)

    model = LogisticRegression(
        solver=str(params.get("solver", "liblinear")),
        max_iter=int(params.get("max_iter", 400)),
        C=float(params.get("C", 1.0)),
        random_state=int(params.get("random_state", 2026)),
    )
    model.fit(x_train, y_train, sample_weight=sample_weight)
    return model


def _train_catboost(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_eval: np.ndarray,
    y_eval: np.ndarray,
    params: Mapping[str, Any],
) -> Any:
    try:
        from catboost import CatBoostClassifier
    except Exception:
        return None

    scale_weight = _scale_pos_weight(y_train)
    model = CatBoostClassifier(
        iterations=int(params.get("iterations", 400)),
        learning_rate=float(params.get("learning_rate", 0.05)),
        depth=int(params.get("depth", 6)),
        loss_function=str(params.get("loss_function", "Logloss")),
        random_seed=int(params.get("random_seed", 2026)),
        verbose=bool(params.get("verbose", False)),
        class_weights=[1.0, scale_weight],
    )
    model.fit(x_train, y_train, eval_set=(x_eval, y_eval), use_best_model=True)
    return model


def _prepare_predict_input(
    model: Any,
    x_matrix: np.ndarray,
    transformed_feature_names: Sequence[str] | None = None,
) -> Any:
    if transformed_feature_names and model.__class__.__module__.startswith("lightgbm"):
        return pd.DataFrame(x_matrix, columns=list(transformed_feature_names))
    return x_matrix


def predict_raw_probability(
    models: Sequence[tuple[str, Any]],
    x_matrix: np.ndarray,
    transformed_feature_names: Sequence[str] | None = None,
) -> np.ndarray:
    all_probs = []
    for _, model in models:
        model_input = _prepare_predict_input(
            model,
            x_matrix,
            transformed_feature_names=transformed_feature_names,
        )
        probs = model.predict_proba(model_input)[:, 1]
        all_probs.append(probs)
    return np.mean(np.vstack(all_probs), axis=0)


def fit_platt_calibrator(raw_prob: np.ndarray, y_true: np.ndarray) -> Any:
    if len(np.unique(y_true)) < 2:
        return IdentityCalibrator()
    calibrator = LogisticRegression(solver="lbfgs")
    calibrator.fit(raw_prob.reshape(-1, 1), y_true)
    return calibrator


def apply_calibration(calibrator: Any, raw_prob: np.ndarray) -> np.ndarray:
    prob = calibrator.predict_proba(raw_prob.reshape(-1, 1))[:, 1]
    return np.clip(prob, 0.0, 1.0)


def build_score_reference(probabilities: np.ndarray) -> np.ndarray:
    """Store a sorted validation distribution to map probabilities into percentile-like risk scores."""
    probs = np.asarray(probabilities, dtype=float)
    probs = probs[np.isfinite(probs)]
    if probs.size == 0:
        return np.asarray([], dtype=float)
    return np.sort(probs)


def to_risk_scores(probabilities: np.ndarray, score_reference: np.ndarray | None = None) -> np.ndarray:
    probs = np.asarray(probabilities, dtype=float)
    reference = None if score_reference is None else np.asarray(score_reference, dtype=float)

    if reference is not None and reference.size > 0:
        positions = np.searchsorted(reference, probs, side="right")
        percentiles = positions / float(reference.size)
        return np.clip(np.rint(percentiles * 100.0), 0, 100).astype(int)

    return np.clip(np.rint(probs * 100.0), 0, 100).astype(int)


def _false_positive_rate(y_true: np.ndarray, predicted_positive: np.ndarray) -> float:
    tn, fp, _, _ = confusion_matrix(y_true, predicted_positive, labels=[0, 1]).ravel()
    denom = tn + fp
    if denom == 0:
        return 0.0
    return float(fp / denom)


def _approve_fraud_rate(y_true: np.ndarray, risk_score: np.ndarray, approve_threshold: int) -> float:
    approved = risk_score < approve_threshold
    if int(approved.sum()) == 0:
        return 0.0
    return float(y_true[approved].mean())


def _approve_share(risk_score: np.ndarray, approve_threshold: int) -> float:
    approved = risk_score < approve_threshold
    if len(risk_score) == 0:
        return 0.0
    return float(approved.mean())


def _flag_share(risk_score: np.ndarray, approve_threshold: int, block_threshold: int) -> float:
    flagged = (risk_score >= approve_threshold) & (risk_score <= block_threshold)
    if len(risk_score) == 0:
        return 0.0
    return float(flagged.mean())


def _block_share(risk_score: np.ndarray, block_threshold: int) -> float:
    blocked = risk_score > block_threshold
    if len(risk_score) == 0:
        return 0.0
    return float(blocked.mean())


def optimize_thresholds(
    y_true: np.ndarray,
    risk_score: np.ndarray,
    default_approve: int,
    default_block: int,
    target_block_fpr: float,
    target_approve_fraud_rate: float,
    min_approve_share: float,
    min_flag_share: float,
    min_block_share: float,
) -> dict[str, int]:
    def candidate_score(approve_threshold: int, block_threshold: int) -> tuple[float, float, int]:
        approve_rate = _approve_fraud_rate(y_true, risk_score, approve_threshold)
        predicted_fraud = (risk_score > block_threshold).astype(int)
        fpr = _false_positive_rate(y_true, predicted_fraud)
        distance = abs(approve_threshold - default_approve) + abs(block_threshold - default_block)
        return (approve_rate + fpr, approve_rate, distance)

    strict_candidates: list[tuple[tuple[float, float, int], int, int]] = []
    relaxed_candidates: list[tuple[tuple[float, float, int], int, int]] = []

    for approve_threshold in range(0, int(default_approve) + 1):
        for block_threshold in range(max(int(default_block), approve_threshold + 1), 101):
            approve_share = _approve_share(risk_score, approve_threshold)
            flag_share = _flag_share(risk_score, approve_threshold, block_threshold)
            block_share = _block_share(risk_score, block_threshold)

            if approve_share < min_approve_share:
                continue
            if flag_share < min_flag_share:
                continue
            if block_share < min_block_share:
                continue

            predicted_fraud = (risk_score > block_threshold).astype(int)
            fpr = _false_positive_rate(y_true, predicted_fraud)
            if fpr > target_block_fpr:
                continue

            score_tuple = candidate_score(approve_threshold, block_threshold)
            relaxed_candidates.append((score_tuple, approve_threshold, block_threshold))

            approve_rate = _approve_fraud_rate(y_true, risk_score, approve_threshold)
            if approve_rate <= target_approve_fraud_rate:
                strict_candidates.append((score_tuple, approve_threshold, block_threshold))

    candidate_pool = strict_candidates or relaxed_candidates
    if candidate_pool:
        _, approve_threshold, block_threshold = min(candidate_pool, key=lambda item: item[0])
        return {
            "approve_threshold": int(approve_threshold),
            "block_threshold": int(block_threshold),
        }

    return {
        "approve_threshold": int(default_approve),
        "block_threshold": int(default_block),
    }


def route_status(score: int, approve_threshold: int, block_threshold: int) -> str:
    if score < approve_threshold:
        return "Approve"
    if score > block_threshold:
        return "Block"
    return "Flag"


def evaluate(
    y_true: np.ndarray,
    calibrated_prob: np.ndarray,
    approve_threshold: int,
    block_threshold: int,
    score_reference: np.ndarray | None = None,
) -> dict[str, Any]:
    risk = to_risk_scores(calibrated_prob, score_reference=score_reference)
    predicted_block = (risk > block_threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, predicted_block, labels=[0, 1]).ravel()

    statuses = [route_status(int(s), approve_threshold, block_threshold) for s in risk]
    route_counts = {
        "Approve": int(sum(1 for s in statuses if s == "Approve")),
        "Flag": int(sum(1 for s in statuses if s == "Flag")),
        "Block": int(sum(1 for s in statuses if s == "Block")),
    }

    metrics = {
        "roc_auc": float(roc_auc_score(y_true, calibrated_prob)),
        "pr_auc": float(average_precision_score(y_true, calibrated_prob)),
        "brier": float(brier_score_loss(y_true, calibrated_prob)),
        "precision_block": float(precision_score(y_true, predicted_block, zero_division=0)),
        "recall_block": float(recall_score(y_true, predicted_block, zero_division=0)),
        "false_positive_rate_block": float(fp / (fp + tn)) if (fp + tn) else 0.0,
        "approve_fraud_rate": float(_approve_fraud_rate(y_true, risk, approve_threshold)),
        "thresholds": {
            "approve_threshold": int(approve_threshold),
            "block_threshold": int(block_threshold),
        },
        "confusion_matrix_block": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
        "route_distribution": route_counts,
    }
    return metrics


def collect_feature_importance(
    models: Sequence[tuple[str, Any]],
    feature_names: Sequence[str],
) -> dict[str, float]:
    if not feature_names:
        return {}

    aggregate = np.zeros(len(feature_names), dtype=float)
    used = 0

    for _, model in models:
        if hasattr(model, "feature_importances_"):
            importance = np.asarray(model.feature_importances_, dtype=float)
        elif hasattr(model, "get_feature_importance"):
            importance = np.asarray(model.get_feature_importance(), dtype=float)
        else:
            continue

        if len(importance) != len(feature_names):
            continue
        if importance.sum() > 0:
            importance = importance / importance.sum()
        aggregate += importance
        used += 1

    if used == 0:
        return {name: 0.0 for name in feature_names}

    aggregate = aggregate / float(used)
    pairs = sorted(zip(feature_names, aggregate), key=lambda x: x[1], reverse=True)
    return {name: float(value) for name, value in pairs}


def train_pipeline(
    frame: pd.DataFrame,
    target_col: str,
    id_col: str,
    time_col: str,
    categorical_candidates: Sequence[str],
    model_cfg: Mapping[str, Any],
    routing_cfg: Mapping[str, Any],
    feature_store: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    dataset = frame.dropna(subset=[target_col]).copy()
    train_df, calib_df, valid_df = split_train_calib_valid(
        dataset,
        time_col=time_col,
        valid_frac=float(model_cfg.get("valid_frac", 0.20)),
        calib_frac=float(model_cfg.get("calib_frac", 0.10)),
    )

    feature_columns = select_feature_columns(dataset, target_col=target_col, id_col=id_col)
    numeric_columns, categorical_columns = infer_column_types(
        train_df,
        feature_columns=feature_columns,
        categorical_candidates=categorical_candidates,
    )

    preprocessor = build_preprocessor(numeric_columns, categorical_columns)

    x_train = preprocessor.fit_transform(train_df[feature_columns])
    x_calib = preprocessor.transform(calib_df[feature_columns])
    x_valid = preprocessor.transform(valid_df[feature_columns])

    y_train = train_df[target_col].astype(int).to_numpy()
    y_calib = calib_df[target_col].astype(int).to_numpy()
    y_valid = valid_df[target_col].astype(int).to_numpy()

    models: list[tuple[str, Any]] = []
    class_weight_mode = str(model_cfg.get("class_weight_mode", "scale_pos_weight"))
    use_lightgbm = bool(model_cfg.get("use_lightgbm", True))

    if use_lightgbm:
        lgb_model = _train_lightgbm(
            x_train,
            y_train,
            x_calib,
            y_calib,
            params=model_cfg.get("lightgbm", {}),
            class_weight_mode=class_weight_mode,
        )
        models.append(("lightgbm", lgb_model))
    else:
        fallback_model = _train_logistic_fallback(
            x_train,
            y_train,
            params=model_cfg.get("logistic_fallback", {}),
            class_weight_mode=class_weight_mode,
        )
        models.append(("logistic_fallback", fallback_model))

    if bool(model_cfg.get("enable_catboost_ensemble", True)):
        cb_model = _train_catboost(
            x_train,
            y_train,
            x_calib,
            y_calib,
            params=model_cfg.get("catboost", {}),
        )
        if cb_model is not None:
            models.append(("catboost", cb_model))

    transformed_feature_names = list(numeric_columns) + list(categorical_columns)

    raw_calib = predict_raw_probability(
        models,
        x_calib,
        transformed_feature_names=transformed_feature_names,
    )
    calibrator_method = str(model_cfg.get("calibrator_method", "platt")).lower()
    if calibrator_method == "identity":
        calibrator = IdentityCalibrator()
    else:
        calibrator = fit_platt_calibrator(raw_calib, y_calib)

    raw_valid = predict_raw_probability(
        models,
        x_valid,
        transformed_feature_names=transformed_feature_names,
    )
    calibrated_valid = apply_calibration(calibrator, raw_valid)
    score_reference = build_score_reference(calibrated_valid)
    risk_valid = to_risk_scores(calibrated_valid, score_reference=score_reference)

    approve_threshold = int(routing_cfg.get("approve_threshold", 70))
    block_threshold = int(routing_cfg.get("block_threshold", 90))

    if bool(routing_cfg.get("optimize_thresholds", True)):
        optimized = optimize_thresholds(
            y_true=y_valid,
            risk_score=risk_valid,
            default_approve=approve_threshold,
            default_block=block_threshold,
            target_block_fpr=float(routing_cfg.get("target_block_fpr", 0.01)),
            target_approve_fraud_rate=float(routing_cfg.get("target_approve_fraud_rate", 0.005)),
            min_approve_share=float(routing_cfg.get("min_approve_share", 0.20)),
            min_flag_share=float(routing_cfg.get("min_flag_share", 0.02)),
            min_block_share=float(routing_cfg.get("min_block_share", 0.002)),
        )
        approve_threshold = optimized["approve_threshold"]
        block_threshold = optimized["block_threshold"]

    metrics = evaluate(
        y_true=y_valid,
        calibrated_prob=calibrated_valid,
        approve_threshold=approve_threshold,
        block_threshold=block_threshold,
        score_reference=score_reference,
    )

    feature_importance = collect_feature_importance(models, transformed_feature_names)

    bundle: dict[str, Any] = {
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "target_col": target_col,
        "id_col": id_col,
        "time_col": time_col,
        "feature_columns": feature_columns,
        "numeric_columns": list(numeric_columns),
        "categorical_columns": list(categorical_columns),
        "transformed_feature_names": transformed_feature_names,
        "preprocessor": preprocessor,
        "models": models,
        "calibrator": calibrator,
        "thresholds": {
            "approve_threshold": int(approve_threshold),
            "block_threshold": int(block_threshold),
        },
        "score_reference": score_reference,
        "feature_store": dict(feature_store),
        "feature_importance": feature_importance,
        "training_summary": {
            "train_rows": int(len(train_df)),
            "calib_rows": int(len(calib_df)),
            "valid_rows": int(len(valid_df)),
            "positive_rate_train": float(y_train.mean()),
            "positive_rate_valid": float(y_valid.mean()),
            "model_names": [name for name, _ in models],
        },
    }

    return bundle, metrics


def save_bundle(bundle: Mapping[str, Any], path: str) -> None:
    joblib.dump(dict(bundle), path)


def load_bundle(path: str) -> dict[str, Any]:
    return joblib.load(path)
