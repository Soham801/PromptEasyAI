from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from .api import analyze_prompt, evaluate_prompt
from .llm import OfflineProvider
from .models import PromptAnalysis


app = FastAPI(title="PromptEasyAI")


class AnalyzeRequest(BaseModel):
    prompt: str


class EvaluateRequest(BaseModel):
    analysis: dict[str, Any]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config")
def config() -> dict[str, str]:
    return {"provider": "offline", "model": "offline-model"}


@app.post("/api/analyze")
def analyze_endpoint(payload: AnalyzeRequest) -> dict[str, Any]:
    analysis = analyze_prompt(payload.prompt, provider=OfflineProvider())
    return analysis.model_dump(mode="json")


@app.post("/api/evaluate")
def evaluate_endpoint(payload: EvaluateRequest) -> dict[str, Any]:
    analysis = PromptAnalysis.model_validate(payload.analysis)
    result = evaluate_prompt(analysis)
    return {"valid": result.valid, "errors": result.errors}
