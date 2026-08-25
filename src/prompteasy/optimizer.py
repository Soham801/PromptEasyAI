from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from .evaluator import EvaluationResult, optimization_evaluation
from .models import PromptAnalysis


@runtime_checkable
class PromptOptimizer(Protocol):
    """Provider-agnostic contract for turning analysis into an optimized prompt."""

    def optimize(self, analysis: PromptAnalysis) -> str:
        ...


@dataclass(frozen=True)
class OptimizationPreferences:
    tone: str | None = None
    audience: str | None = None
    domain: str | None = None


class ProviderPromptOptimizer:
    """Generate an optimized prompt through the shared provider abstraction."""

    def __init__(
        self,
        provider: Any,
        preferences: OptimizationPreferences | None = None,
    ) -> None:
        self.provider = provider
        self.preferences = preferences or OptimizationPreferences()

    def optimize(self, analysis: PromptAnalysis) -> str:
        if not isinstance(analysis, PromptAnalysis):
            raise TypeError("analysis must be a PromptAnalysis instance.")

        response = self.provider.generate(
            model=self.provider.model,
            messages=[
                {"role": "system", "content": _build_optimizer_instruction(analysis, self.preferences)},
                {"role": "user", "content": _build_optimizer_input(analysis)},
            ],
        )
        content = response.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("The optimizer returned an empty prompt.")

        optimized_prompt = content.strip()
        result = optimization_evaluation(analysis, optimized_prompt)
        if not result.valid:
            raise ValueError(
                "Optimized prompt failed validation: " + "; ".join(result.errors)
            )

        return optimized_prompt


def select_optimization_strategy(analysis: PromptAnalysis) -> str:
    """Choose a deterministic optimization mode from the analysis signals."""
    if len(analysis.missing_information) >= 2:
        return "question-first"
    if analysis.constraints:
        return "constraint-first"
    if analysis.output_requirements:
        return "format-first"
    if any(
        marker in analysis.task.lower()
        for marker in ("reason", "analyze", "evaluate", "explain why")
    ):
        return "reasoning-first"
    return "direct"


def _build_optimizer_instruction(
    analysis: PromptAnalysis,
    preferences: OptimizationPreferences,
) -> str:
    strategy = select_optimization_strategy(analysis)
    preference_lines = []
    for label, value in (
        ("audience", preferences.audience),
        ("tone", preferences.tone),
        ("domain", preferences.domain),
    ):
        if value and value not in {"general", "neutral"}:
            preference_lines.append(f"Use {label}: {value}.")

    strategy_lines = {
        "question-first": "Use question-first mode: ask for the highest-impact missing details before suggesting optional defaults.",
        "constraint-first": "Use constraint-first mode: make every explicit restriction prominent and preserve it exactly.",
        "format-first": "Use format-first mode: make the requested output structure explicit and preserve it exactly.",
        "reasoning-first": "Use reasoning-first mode: clarify the requested reasoning or evaluation criteria without answering the task.",
        "direct": "Use direct optimization: make the request actionable without inventing user-specific facts.",
    }
    strategy_line = strategy_lines[strategy]
    return OPTIMIZER_INSTRUCTION + "\n\n" + strategy_line + "\n" + " ".join(preference_lines)


def _build_optimizer_input(analysis: PromptAnalysis) -> str:
    return (
        f"Original prompt:\n{analysis.original_prompt}\n\n"
        f"Intent:\n{analysis.intent}\n\n"
        f"Task:\n{analysis.task}\n\n"
        f"Context:\n{_format_items(analysis.context)}\n\n"
        f"Constraints:\n{_format_items(analysis.constraints)}\n\n"
        f"Output requirements:\n{_format_items(analysis.output_requirements)}\n\n"
        f"Ambiguities:\n{_format_items(analysis.ambiguities)}\n\n"
        f"Missing information:\n{_format_items(analysis.missing_information)}"
    )


def _format_items(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "- None provided"


OPTIMIZER_INSTRUCTION = """
You are PromptEasy's Prompt Optimizer.

Return only an improved prompt for the downstream AI system. Do not
answer the user's task.

Preserve the original intent, task, explicit constraints, and requested
output format. Make ambiguity explicit with a placeholder or question.
Do not invent facts, context, requirements, names, numbers, or tools.
Do not add details merely to make the prompt longer.
""".strip()
