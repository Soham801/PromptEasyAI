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

    if not analysis.original_prompt.strip():
        errors.append("original_prompt is empty")