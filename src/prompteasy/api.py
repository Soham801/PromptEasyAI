from __future__ import annotations

from typing import Any

from .analyzer import PromptAnalyzer
from .config import get_settings
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

    settings = get_settings()
    configured = settings.provider

    if configured == "groq":
        return {
            "provider": "groq",
            "model": settings.model,
        }

    return {"provider": "offline", "model": settings.model}


def _build_default_provider() -> Any:
    settings = get_settings()
    configured = settings.provider

    if configured == "groq":
        return GroqProvider(model=settings.model)

    return OfflineProvider(model=settings.model)
