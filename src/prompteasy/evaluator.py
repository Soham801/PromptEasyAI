import re
from dataclasses import dataclass, field
from typing import Any

from .models import PromptAnalysis


@dataclass(frozen=True)
class EvaluationResult:
    valid: bool
    errors: list[str]


@dataclass(frozen=True)
class EvaluationExample:
    prompt: str
    expected_intent: str
    expected_task: str
    category: str
    difficulty: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationDataset:
    version: str
    examples: list[EvaluationExample]


@dataclass(frozen=True)
class EvaluationReport:
    passed: int
    failed: int
    pass_rate: float
    by_category: dict[str, float]
    by_difficulty: dict[str, float]


def _tokenize(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9']+", (value or "").lower())
        if len(token) > 2
    }


def _similarity(left: str, right: str) -> float:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    union = left_tokens | right_tokens
    if not union:
        return 0.0
    return len(left_tokens & right_tokens) / len(union)


def structural_evaluation(analysis: PromptAnalysis) -> EvaluationResult:
    errors: list[str] = []

    required_text_fields = [
        "original_prompt",
        "intent",
        "task",
        "optimized_prompt",
    ]

    for field_name in required_text_fields:
        value = getattr(analysis, field_name)
        if not isinstance(value, str):
            errors.append(f"{field_name} must be a string")
        elif not value.strip():
            errors.append(f"{field_name} is empty")

    list_fields = [
        "context",
        "constraints",
        "output_requirements",
        "ambiguities",
        "missing_information",
        "optimization_opportunities",
    ]

    for field_name in list_fields:
        value = getattr(analysis, field_name)
        if not isinstance(value, list):
            errors.append(f"{field_name} must be a list")
            continue

        for index, item in enumerate(value):
            if not isinstance(item, str):
                errors.append(
                    f"{field_name} must contain only strings; item {index} is not a string"
                )
            elif not item.strip():
                errors.append(f"{field_name} contains an empty string at index {index}")

    return EvaluationResult(
        valid=len(errors) == 0,
        errors=errors,
    )


def semantic_evaluation(analysis: PromptAnalysis) -> EvaluationResult:
    errors: list[str] = []

    original = analysis.original_prompt
    intent = analysis.intent
    task = analysis.task
    optimized = analysis.optimized_prompt

    intent_overlap = _similarity(original, intent)
    task_overlap = _similarity(original, task)
    optimized_overlap = _similarity(original, optimized)

    if intent_overlap < 0.15 and task_overlap < 0.15:
        errors.append("intent and task are not materially related to the original prompt")

    if optimized_overlap < 0.15:
        errors.append("optimized_prompt is not materially related to the original prompt")

    return EvaluationResult(
        valid=len(errors) == 0,
        errors=errors,
    )


def optimization_evaluation(
    analysis: PromptAnalysis,
    optimized_prompt: str | None = None,
) -> EvaluationResult:
    """Check that optimization preserves requirements without adding facts."""

    errors: list[str] = []
    optimized = optimized_prompt or analysis.optimized_prompt

    if _similarity(analysis.original_prompt, optimized) < 0.15:
        errors.append("optimized_prompt is not materially related to the original prompt")

    source = " ".join(
        [
            analysis.original_prompt,
            *analysis.context,
            *analysis.constraints,
            *analysis.output_requirements,
        ]
    )

    source_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", source))
    optimized_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", optimized))
    unsupported_numbers = optimized_numbers - source_numbers
    if unsupported_numbers:
        errors.append(
            "optimized_prompt adds unsupported numeric details: "
            + ", ".join(sorted(unsupported_numbers))
        )

    source_quotes = set(re.findall(r"['\"]([^'\"]+)['\"]", source))
    optimized_quotes = set(re.findall(r"['\"]([^'\"]+)['\"]", optimized))
    unsupported_quotes = optimized_quotes - source_quotes
    if unsupported_quotes:
        errors.append("optimized_prompt adds unsupported quoted details")

    for requirement in [*analysis.constraints, *analysis.output_requirements]:
        if _is_explicit_requirement(requirement) and not _requirement_is_preserved(
            requirement, optimized
        ):
            errors.append(f"optimized_prompt does not preserve requirement: {requirement}")

    return EvaluationResult(valid=len(errors) == 0, errors=errors)


def _is_explicit_requirement(requirement: str) -> bool:
    lowered = requirement.lower()
    markers = (
        "must",
        "do not",
        "don't",
        "only",
        "exactly",
        "format",
        "json",
        "xml",
        "yaml",
        "table",
        "bullet",
        "maximum",
        "minimum",
        "limit",
    )
    return any(marker in lowered for marker in markers)


def _requirement_is_preserved(requirement: str, optimized: str) -> bool:
    requirement_tokens = _tokenize(requirement)
    optimized_tokens = _tokenize(optimized)
    if not requirement_tokens:
        return True
    return len(requirement_tokens & optimized_tokens) / len(requirement_tokens) >= 0.5


def evaluate_analysis(analysis: PromptAnalysis) -> EvaluationResult:
    structural = structural_evaluation(analysis)
    semantic = semantic_evaluation(analysis)
    optimization = (
        optimization_evaluation(analysis)
        if structural.valid
        else EvaluationResult(valid=False, errors=[])
    )

    errors = structural.errors + semantic.errors + optimization.errors
    return EvaluationResult(
        valid=structural.valid and semantic.valid and optimization.valid,
        errors=errors,
    )


def create_evaluation_dataset() -> EvaluationDataset:
    examples = [
        EvaluationExample(
            prompt="Explain machine learning in simple terms.",
            expected_intent="Understand machine learning",
            expected_task="Explain machine learning",
            category="simple",
            difficulty="easy",
        ),
        EvaluationExample(
            prompt="Compare Redis and Postgres for an analytics pipeline.",
            expected_intent="Choose a database for analytics",
            expected_task="Compare Redis and Postgres",
            category="technical",
            difficulty="medium",
        ),
        EvaluationExample(
            prompt="Help me write a better product brief.",
            expected_intent="Improve a product brief",
            expected_task="Refine a product brief",
            category="ambiguous",
            difficulty="medium",
        ),
        EvaluationExample(
            prompt="Write a Python function to paginate API results.",
            expected_intent="Implement pagination in Python",
            expected_task="Write a Python pagination function",
            category="coding",
            difficulty="hard",
        ),
        EvaluationExample(
            prompt="Act as a senior PM and prioritize a roadmap.",
            expected_intent="Prioritize a roadmap",
            expected_task="Create a product roadmap",
            category="role-based",
            difficulty="medium",
        ),
        EvaluationExample(
            prompt="Summarize this long incident report and list the main actions we should take next.",
            expected_intent="Summarize an incident report",
            expected_task="Summarize and identify next steps",
            category="long",
            difficulty="hard",
        ),
    ]

    return EvaluationDataset(version="1.0", examples=examples)
