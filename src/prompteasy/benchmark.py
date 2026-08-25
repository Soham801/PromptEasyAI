from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .api import analyze_prompt
from .evaluator import EvaluationDataset, _similarity, create_evaluation_dataset, evaluate_analysis, optimization_evaluation
from .models import PromptAnalysis


BENCHMARK_THRESHOLD = 0.80


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    category: str
    difficulty: str
    structural_valid: bool
    semantic_valid: bool
    requirement_retention: bool
    ambiguity_handled: bool
    hallucination_risk: bool
    intent_alignment: float
    task_alignment: float


@dataclass(frozen=True)
class BenchmarkReport:
    dataset_version: str
    provider: str
    model: str
    total: int
    passed: int
    failed: int
    pass_rate: float
    metrics: dict[str, float]
    by_category: dict[str, float]
    by_difficulty: dict[str, float]
    cases: list[BenchmarkCase]

    @property
    def release_gate_passed(self) -> bool:
        return self.pass_rate >= BENCHMARK_THRESHOLD and self.metrics["hallucination_risk"] == 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"release_gate_passed": self.release_gate_passed}


def run_benchmark(
    provider: Any | None = None,
    dataset: EvaluationDataset | None = None,
) -> BenchmarkReport:
    dataset = dataset or create_evaluation_dataset()
    cases: list[BenchmarkCase] = []

    for example in dataset.examples:
        analysis = analyze_prompt(example.prompt, provider=provider)
        cases.append(_evaluate_case(example, analysis))

    passed = sum(
        case.structural_valid
        and case.semantic_valid
        and case.requirement_retention
        and case.ambiguity_handled
        and not case.hallucination_risk
        for case in cases
    )
    total = len(cases)
    return BenchmarkReport(
        dataset_version=dataset.version,
        provider=_provider_name(provider),
        model=getattr(provider, "model", "offline-model"),
        total=total,
        passed=passed,
        failed=total - passed,
        pass_rate=passed / total if total else 0.0,
        metrics=_aggregate_metrics(cases),
        by_category=_group_pass_rates(cases, dataset, "category"),
        by_difficulty=_group_pass_rates(cases, dataset, "difficulty"),
        cases=cases,
    )


def _evaluate_case(example: Any, analysis: PromptAnalysis) -> BenchmarkCase:
    structural = evaluate_analysis(analysis)
    optimization = optimization_evaluation(analysis)
    optimized = analysis.optimized_prompt.lower()
    ambiguity_handled = not analysis.missing_information or any(
        marker in optimized for marker in ("ask for", "missing", "clarif", "question")
    )
    return BenchmarkCase(
        name=getattr(example, "name", example.prompt[:32]),
        category=example.category,
        difficulty=example.difficulty,
        structural_valid=structural.valid,
        semantic_valid=not any("materially related" in error for error in structural.errors),
        requirement_retention=optimization.valid,
        ambiguity_handled=ambiguity_handled,
        hallucination_risk=any("unsupported" in error for error in optimization.errors),
        intent_alignment=_similarity(example.expected_intent, analysis.intent),
        task_alignment=_similarity(example.expected_task, analysis.task),
    )


def _aggregate_metrics(cases: list[BenchmarkCase]) -> dict[str, float]:
    total = len(cases) or 1
    return {
        "structural_validity": sum(case.structural_valid for case in cases) / total,
        "semantic_validity": sum(case.semantic_valid for case in cases) / total,
        "requirement_retention": sum(case.requirement_retention for case in cases) / total,
        "ambiguity_handling": sum(case.ambiguity_handled for case in cases) / total,
        "hallucination_risk": sum(case.hallucination_risk for case in cases) / total,
        "intent_alignment": sum(case.intent_alignment for case in cases) / total,
        "task_alignment": sum(case.task_alignment for case in cases) / total,
    }


def _group_pass_rates(cases: list[BenchmarkCase], dataset: EvaluationDataset, field: str) -> dict[str, float]:
    rates: dict[str, list[bool]] = {}
    for case in cases:
        key = getattr(case, field)
        rates.setdefault(key, []).append(case.structural_valid and case.semantic_valid and case.requirement_retention)
    return {key: sum(values) / len(values) for key, values in rates.items()}


def _provider_name(provider: Any | None) -> str:
    return provider.__class__.__name__.replace("Provider", "").lower() if provider else "offline"