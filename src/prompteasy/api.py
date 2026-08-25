from __future__ import annotations

import os
from typing import Any

from .analyzer import PromptAnalyzer
from .evaluator import evaluate_analysis, optimization_evaluation
from .llm import GroqProvider, OfflineProvider
from .models import PromptAnalysis
from .optimizer import OptimizationPreferences, ProviderPromptOptimizer


def analyze_prompt(
    prompt: str,
    provider: Any | None = None,
    preferences: OptimizationPreferences | None = None,
) -> PromptAnalysis:
    resolved_provider = provider or _build_default_provider()
    analyzer = PromptAnalyzer(provider=resolved_provider)
    analysis = analyzer.analyze(prompt)

    try:
        optimized_prompt = ProviderPromptOptimizer(
            resolved_provider,
            preferences=preferences,
        ).optimize(analysis)
        return analysis.model_copy(update={"optimized_prompt": optimized_prompt})
    except Exception as exc:
        fallback_result = optimization_evaluation(analysis)
        if fallback_result.valid:
            return analysis
        raise ValueError(
            "Prompt optimization failed validation: " + "; ".join(fallback_result.errors)
        ) from exc


def evaluate_prompt(analysis: PromptAnalysis):
    return evaluate_analysis(analysis)


def optimize_prompt(analysis: PromptAnalysis, provider: Any | None = None) -> str:
    if provider is None:
        result = optimization_evaluation(analysis)
        if not result.valid:
            raise ValueError(
                "Optimized prompt failed validation: " + "; ".join(result.errors)
            )
        return analysis.optimized_prompt

    return ProviderPromptOptimizer(provider).optimize(analysis)


def get_provider_config(provider: Any | None = None) -> dict[str, str]:
    if provider is not None:
        return {
            "provider": provider.__class__.__name__.replace("Provider", "").lower(),
            "model": getattr(provider, "model", "unknown"),
        }

    configured = os.getenv("PROMPTEASY_PROVIDER", "offline").strip().lower()
    if configured not in {"offline", "groq"}:
        configured = "offline"

    if configured == "groq":
        return {
            "provider": "groq",
            "model": os.getenv("PROMPTEASY_MODEL", "openai/gpt-oss-20b"),
        }

    return {"provider": "offline", "model": "offline-model"}


def _build_default_provider() -> Any:
    configured = os.getenv("PROMPTEASY_PROVIDER", "offline").strip().lower()

    if configured == "groq":
        model = os.getenv("PROMPTEASY_MODEL", "openai/gpt-oss-20b")
        return GroqProvider(model=model)

    return OfflineProvider()
