from __future__ import annotations

import re
from typing import Any, Protocol, runtime_checkable

from .evaluator import EvaluationResult, optimization_evaluation
from .models import PromptAnalysis


@runtime_checkable
class PromptOptimizer(Protocol):
    """Provider-agnostic contract for turning analysis into an optimized prompt."""

    def optimize(self, analysis: PromptAnalysis) -> str:
        ...


class ProviderPromptOptimizer:
    """Generate an optimized prompt through the shared provider abstraction."""

    def __init__(self, provider: Any) -> None:
        self.provider = provider

    def optimize(self, analysis: PromptAnalysis) -> str:
        if not isinstance(analysis, PromptAnalysis):
            raise TypeError("analysis must be a PromptAnalysis instance.")

        response = self.provider.generate(
            model=self.provider.model,
            messages=[
                {"role": "system", "content": OPTIMIZER_INSTRUCTION},
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
