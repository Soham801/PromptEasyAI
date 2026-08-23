from dataclasses import dataclass

from .models import PromptAnalysis


@dataclass(frozen=True)
class EvaluationResult:
    valid: bool
    errors: list[str]


def evaluate_analysis(
    analysis: PromptAnalysis,
) -> EvaluationResult:
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