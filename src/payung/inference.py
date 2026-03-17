"""Online inference logic for PocketSignal.

This module turns a raw transaction payload into:
- a calibrated risk score
- an Approve / Flag / Block route
- human-readable reasons
- a local recovery explanation for Flag cases
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from .llm import OllamaClient, fallback_flag_message, normalize_language, normalize_response_profile
from .modeling import apply_calibration, load_bundle, predict_raw_probability, route_status, to_risk_scores
from .preprocess import apply_feature_store, ensure_columns


@dataclass
class PredictionResult:
    status: str
    risk_score: int
    probability: float
    top_features: list[str]
    explanation: str


def friendly_feature_reason(feature: str) -> str:
    """Map technical feature names into presentation-safe semantic reasons."""
    name = str(feature or "").strip()
    lower = name.lower()

    if lower in {"transactionamt", "card1_amt_mean_past"}:
        return "unusual amount pattern"
    if lower in {"transactiondt", "hour", "day"}:
        return "unusual transaction timing"
    if lower in {"card1_device_degree", "card1_email_degree"}:
        return "shared fraud network linkage"
    if lower in {"deviceinfo", "devicetype", "id-30", "id-31", "id-32", "id-33"}:
        return "unusual device or browser context"
    if lower in {"p_emaildomain", "r_emaildomain", "p_emaildomain".lower(), "r_emaildomain".lower()}:
        return "email identity mismatch"
    if lower.startswith("dist") or lower.startswith("addr"):
        return "location or address anomaly"
    if lower.startswith("card"):
        return "payment card pattern"
    if lower.startswith("c"):
        return "historical activity pattern"
    if lower.startswith("d"):
        return "timing or account age pattern"
    if lower.startswith("m"):
        return "identity consistency signal"
    if lower.startswith("v"):
        return "transaction consistency signal"
    if lower.startswith("id-"):
        return "identity verification context"
    return "transaction behavior signal"


class PayungPredictor:
    def __init__(self, bundle: Mapping[str, Any]) -> None:
        self.bundle = dict(bundle)

    @classmethod
    def from_path(cls, bundle_path: str) -> "PayungPredictor":
        bundle = load_bundle(bundle_path)
        return cls(bundle=bundle)

    def _build_feature_frame_from_raw(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Apply the saved feature store so online inference matches offline training features."""
        raw = raw.copy()
        time_col = self.bundle.get("time_col", "TransactionDT")
        if time_col not in raw.columns:
            raw[time_col] = np.nan

        enriched = apply_feature_store(raw, self.bundle.get("feature_store", {}))
        feature_columns: Sequence[str] = self.bundle.get("feature_columns", [])
        completed = ensure_columns(enriched, feature_columns)
        return completed[list(feature_columns)]

    def _build_feature_frame(self, payload: Mapping[str, Any]) -> pd.DataFrame:
        return self._build_feature_frame_from_raw(pd.DataFrame([dict(payload)]))

    def _transformed_feature_names(self) -> list[str] | None:
        explicit = self.bundle.get("transformed_feature_names")
        if explicit:
            return list(explicit)

        numeric_columns = list(self.bundle.get("numeric_columns", []))
        categorical_columns = list(self.bundle.get("categorical_columns", []))
        derived = numeric_columns + categorical_columns
        return derived or None

    def _select_top_features(self, row: pd.Series, top_k: int = 3) -> list[str]:
        """Select diverse semantic reasons rather than repeating raw technical feature names."""
        importance: Mapping[str, float] = self.bundle.get("feature_importance", {})
        ordered = sorted(importance.items(), key=lambda item: item[1], reverse=True)

        selected: list[str] = []
        seen: set[str] = set()
        for feature, _ in ordered:
            if feature not in row.index:
                continue
            value = row[feature]
            if pd.isna(value):
                continue
            label = friendly_feature_reason(feature)
            if label in seen:
                continue
            selected.append(label)
            seen.add(label)
            if len(selected) >= top_k:
                break

        if selected:
            return selected
        fallback: list[str] = []
        for name, _ in ordered:
            label = friendly_feature_reason(name)
            if label in fallback:
                continue
            fallback.append(label)
            if len(fallback) >= top_k:
                break
        return fallback

    @staticmethod
    def _default_explanation(status: str, top_features: Sequence[str]) -> str:
        feature_text = ", ".join(top_features) if top_features else "transaction behavior"
        if status == "Approve":
            return (
                "Approved automatically because this payment fits a low-risk pattern. "
                f"Main monitored signals: {feature_text}."
            )
        if status == "Block":
            return (
                "Blocked because the payment shows multiple strong fraud indicators. "
                f"Main drivers: {feature_text}."
            )
        return (
            "Flagged for review because the payment looks unusual, but not certain fraud yet. "
            f"Main drivers: {feature_text}."
        )

    def predict_batch(
        self,
        payloads: Sequence[Mapping[str, Any]],
        llm_client: OllamaClient | None = None,
    ) -> list[PredictionResult]:
        if not payloads:
            return []

        frame = self._build_feature_frame_from_raw(pd.DataFrame([dict(payload) for payload in payloads]))
        preprocessor = self.bundle["preprocessor"]
        models = self.bundle["models"]
        calibrator = self.bundle["calibrator"]

        x_matrix = preprocessor.transform(frame)
        raw_prob = predict_raw_probability(
            models,
            x_matrix,
            transformed_feature_names=self._transformed_feature_names(),
        )
        calibrated = apply_calibration(calibrator, raw_prob)
        risk_scores = to_risk_scores(calibrated, score_reference=self.bundle.get("score_reference"))

        thresholds = self.bundle.get("thresholds", {})
        approve_threshold = int(thresholds.get("approve_threshold", 70))
        block_threshold = int(thresholds.get("block_threshold", 90))
        results: list[PredictionResult] = []

        for index, payload in enumerate(payloads):
            risk_score = int(risk_scores[index])
            probability = float(calibrated[index])
            status = route_status(
                risk_score,
                approve_threshold=approve_threshold,
                block_threshold=block_threshold,
            )

            top_features = self._select_top_features(frame.iloc[index], top_k=3)
            explanation = self._default_explanation(status=status, top_features=top_features)
            language = normalize_language(payload.get("preferred_language"))
            response_profile = normalize_response_profile(payload.get("response_profile"))

            if status == "Flag" and llm_client is not None:
                transaction_amt = payload.get("TransactionAmt")
                try:
                    transaction_amt = float(transaction_amt) if transaction_amt is not None else None
                except (TypeError, ValueError):
                    transaction_amt = None
                # PocketSignal supports two local recovery strategies:
                # a deterministic fast route and a richer local wording route.
                if response_profile == "fast_route":
                    explanation = fallback_flag_message(language=language, transaction_amt=transaction_amt)
                else:
                    explanation = llm_client.explain_flag(
                        transaction_amt=transaction_amt,
                        top_features=top_features,
                        language=language,
                    )
            elif status == "Flag":
                transaction_amt = payload.get("TransactionAmt")
                try:
                    transaction_amt = float(transaction_amt) if transaction_amt is not None else None
                except (TypeError, ValueError):
                    transaction_amt = None
                explanation = fallback_flag_message(language=language, transaction_amt=transaction_amt)

            results.append(
                PredictionResult(
                    status=status,
                    risk_score=risk_score,
                    probability=probability,
                    top_features=list(top_features),
                    explanation=explanation,
                )
            )

        return results

    def predict(self, payload: Mapping[str, Any], llm_client: OllamaClient | None = None) -> PredictionResult:
        return self.predict_batch([payload], llm_client=llm_client)[0]
