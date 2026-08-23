from __future__ import annotations

from typing import Any

from .analyzer import PromptAnalyzer
from .evaluator import evaluate_analysis
from .llm import OfflineProvider
from .models import PromptAnalysis


def analyze_prompt(prompt: str, provider: Any | None = None) -> PromptAnalysis:
    analyzer = PromptAnalyzer(provider=provider or OfflineProvider())
    return analyzer.analyze(prompt)


def evaluate_prompt(analysis: PromptAnalysis):
    return evaluate_analysis(analysis)
