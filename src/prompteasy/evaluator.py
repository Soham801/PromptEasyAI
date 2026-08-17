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
    if not analysis.intent.strip():
        errors.append("intent is empty")
    if not analysis.task.strip():
        errors.append("task is empty")
    if not isinstance(analysis.constraints,list):
        errors.append("constraints must be a list")
    if not isinstance(analysis.ambiguities,list):
        errors.append("ambiguities must be a list")
    if not isinstance(analysis.missing_information,list):
        errors.append("missing_information must be a list")
    if not isinstance(analysis.optimization_oppotunities,list):
        errors.append("optimization_opportunities must be a list")

    return EvaluationResult(
        valid=len(errors)==0,
        errors=errors
    )