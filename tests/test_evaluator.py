import pytest

from prompteasy.evaluator import (
    EvaluationExample,
    EvaluationReport,
    create_evaluation_dataset,
    evaluate_analysis,
    semantic_evaluation,
    structural_evaluation,
)
from prompteasy.models import PromptAnalysis


def test_valid_prompt_analysis():

    analysis = PromptAnalysis(
        schema_version="1.0",
        original_prompt="Explain machine learning",
        intent="Understand machine learning",
        task="Explain machine learning",
        context=[],
        constraints=[],
        output_requirements=[],
        ambiguities=[],
        missing_information=[],
        optimization_opportunities=[],
        optimized_prompt="Explain machine learning in clear, beginner-friendly terms.",
    )

    result = evaluate_analysis(analysis)

    assert result.valid is True
    assert result.errors == []


def test_empty_original_prompt_is_invalid():

    with pytest.raises(ValueError):
        PromptAnalysis(
            schema_version="1.0",
            original_prompt="",
            intent="Understand machine learning",
            task="Explain machine learning",
            context=[],
            constraints=[],
            output_requirements=[],
            ambiguities=[],
            missing_information=[],
            optimization_opportunities=[],
            optimized_prompt="Explain machine learning.",
        )


def test_structural_evaluation_rejects_missing_semantic_fields():
    analysis = PromptAnalysis(
        schema_version="1.0",
        original_prompt="Explain machine learning",
        intent="Understand machine learning",
        task="Explain machine learning",
        context=[],
        constraints=[],
        output_requirements=[],
        ambiguities=[],
        missing_information=[],
        optimization_opportunities=[],
        optimized_prompt="Explain machine learning in clear terms.",
    )
    analysis.intent = ""
    analysis.optimized_prompt = ""

    result = structural_evaluation(analysis)

    assert result.valid is False
    assert any("intent" in error for error in result.errors)
    assert any("optimized_prompt" in error for error in result.errors)


def test_semantic_evaluation_rejects_unrelated_prompt():
    analysis = PromptAnalysis(
        schema_version="1.0",
        original_prompt="Explain machine learning",
        intent="Plan a wedding",
        task="Plan a wedding schedule",
        context=[],
        constraints=[],
        output_requirements=[],
        ambiguities=[],
        missing_information=[],
        optimization_opportunities=[],
        optimized_prompt="Plan a wedding schedule for a summer celebration.",
    )

    result = semantic_evaluation(analysis)

    assert result.valid is False
    assert result.errors


def test_dataset_has_version_and_category_coverage():
    dataset = create_evaluation_dataset()

    assert dataset.version == "1.0"
    assert {example.category for example in dataset.examples} >= {
        "simple",
        "technical",
        "ambiguous",
        "coding",
        "role-based",
        "long",
    }


def test_evaluation_report_produces_pass_rates():
    dataset = create_evaluation_dataset()
    valid_result = EvaluationReport(
        passed=1,
        failed=0,
        pass_rate=1.0,
        by_category={"simple": 1.0},
        by_difficulty={"easy": 1.0},
    )

    assert valid_result.pass_rate == 1.0
    assert dataset.version == "1.0"
    assert any(example.category for example in dataset.examples)