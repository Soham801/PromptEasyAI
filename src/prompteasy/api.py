from __future__ import annotations

from typing import Any

from .analyzer import PromptAnalyzer
from .evaluator import evaluate_analysis, optimization_evaluation
from .llm import OfflineProvider
from .models import PromptAnalysis
from .optimizer import ProviderPromptOptimizer


def analyze_prompt(prompt: str, provider: Any | None = None) -> PromptAnalysis:
    analyzer = PromptAnalyzer(provider=provider or OfflineProvider())
    return analyzer.analyze(prompt)


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
