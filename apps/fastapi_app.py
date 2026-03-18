"""PocketSignal FastAPI service for Team Cache Me.

This app exposes the judge-facing API:
- /health for readiness checks
- /predict for calibrated Approve / Flag / Block decisions
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from payung.inference import PayungPredictor
from payung.llm import OllamaClient


class PredictRequest(BaseModel):
    TransactionID: int | None = None
    TransactionDT: float | None = None
    TransactionAmt: float | None = None
    ProductCD: str | None = None
    card1: float | None = None
    card2: float | None = None
    card3: float | None = None
    card4: str | None = None
    card5: float | None = None
    card6: str | None = None
    addr1: float | None = None
    addr2: float | None = None
    P_emaildomain: str | None = None
    R_emaildomain: str | None = None
    DeviceType: str | None = None
    DeviceInfo: str | None = None
    preferred_language: str | None = None
    response_profile: str | None = None
    low_literacy: bool | None = None

    class Config:
        extra = "allow"


class PredictResponse(BaseModel):
    status: str = Field(..., description="Approve | Flag | Block")
    risk_score: int = Field(..., ge=0, le=100)
    probability: float = Field(..., ge=0.0, le=1.0)
    top_features: list[str]
    explanation: str
    latency_ms: float
    model_version: str


class HealthResponse(BaseModel):
    model_loaded: bool
    ollama_ready: bool
    feature_store_ready: bool


def _request_payload(data: PredictRequest) -> dict[str, Any]:
    if hasattr(data, "model_dump"):
        payload = data.model_dump(exclude_none=True)
        extras = getattr(data, "model_extra", None) or {}
        payload.update(extras)
        return payload
    payload = data.dict(exclude_none=True)
    return payload


app = FastAPI(title="PocketSignal Risk API", version="1.0.0")

def _env(primary: str, legacy: str, default: str) -> str:
    return os.getenv(primary, os.getenv(legacy, default))


MODEL_BUNDLE_PATH = Path(_env("POCKETSIGNAL_MODEL_BUNDLE", "AEGIS_MODEL_BUNDLE", str(ROOT / "artifacts" / "model_bundle.pkl")))
OLLAMA_ENABLED = _env("POCKETSIGNAL_LLM_ENABLED", "AEGIS_LLM_ENABLED", "1") != "0"
OLLAMA_BASE_URL = _env("POCKETSIGNAL_OLLAMA_BASE_URL", "AEGIS_OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = _env("POCKETSIGNAL_OLLAMA_MODEL", "AEGIS_OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT = float(_env("POCKETSIGNAL_OLLAMA_TIMEOUT", "AEGIS_OLLAMA_TIMEOUT", "5.0"))
OLLAMA_KEEP_ALIVE = _env("POCKETSIGNAL_OLLAMA_KEEP_ALIVE", "AEGIS_OLLAMA_KEEP_ALIVE", "10m")
OLLAMA_PRELOAD = _env("POCKETSIGNAL_OLLAMA_PRELOAD", "AEGIS_OLLAMA_PRELOAD", "0") != "0"
RESPONSE_PROFILE_DEFAULT = _env("POCKETSIGNAL_RESPONSE_PROFILE", "AEGIS_RESPONSE_PROFILE", "judge_demo")

predictor: PayungPredictor | None = None
llm_client: OllamaClient | None = None


@app.on_event("startup")
def _startup() -> None:
    global predictor
    global llm_client

    if MODEL_BUNDLE_PATH.exists():
        predictor = PayungPredictor.from_path(str(MODEL_BUNDLE_PATH))
    else:
        predictor = None

    if OLLAMA_ENABLED:
        llm_client = OllamaClient(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            timeout_seconds=OLLAMA_TIMEOUT,
            keep_alive=OLLAMA_KEEP_ALIVE,
        )
        # Optional preload keeps the richer local wording model warm between demo calls.
        if OLLAMA_PRELOAD and llm_client.is_ready():
            llm_client.preload()
    else:
        llm_client = None


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    model_loaded = predictor is not None
    feature_ready = bool(model_loaded and predictor.bundle.get("feature_store"))

    ollama_ready = False
    if llm_client is not None:
        ollama_ready = llm_client.is_ready()

    return HealthResponse(
        model_loaded=model_loaded,
        ollama_ready=ollama_ready,
        feature_store_ready=feature_ready,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model bundle not found. Run scripts/train.py first.")

    request_data = _request_payload(payload)
    request_data.setdefault("response_profile", RESPONSE_PROFILE_DEFAULT)
    started = time.perf_counter()
    result = predictor.predict(request_data, llm_client=llm_client)
    latency_ms = (time.perf_counter() - started) * 1000.0

    return PredictResponse(
        status=result.status,
        risk_score=result.risk_score,
        probability=result.probability,
        top_features=result.top_features,
        explanation=result.explanation,
        latency_ms=round(latency_ms, 3),
        model_version=str(predictor.bundle.get("created_at", "unknown")),
    )
