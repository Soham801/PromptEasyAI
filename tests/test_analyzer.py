from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from prompteasy import PromptAnalyzer
from prompteasy.evaluator import evaluate_analysis
from prompteasy.models import PromptAnalysis


class FakeProvider:
    model = "test-model"

    def __init__(self, content):
        self.client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kwargs: SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(content=content)
                            )
                        ]
                    )
                )
            )
        )


def test_analyzer_returns_optimized_prompt():
    content = '{"schema_version":"1.0","original_prompt":"Explain ML","intent":"Learn ML","task":"Explain machine learning","context":[],"constraints":[],"output_requirements":[],"ambiguities":[],"missing_information":[],"optimization_opportunities":["Specify the audience"],"optimized_prompt":"Explain machine learning to a beginner using one practical example."}'

    result = PromptAnalyzer(FakeProvider(content)).analyze("Explain ML")

    assert result.original_prompt == "Explain ML"
    assert result.schema_version == "1.0"
    assert result.optimized_prompt.startswith("Explain machine learning")

def test_analyzer_accepts_valid_prompt():
    content = '{"schema_version":"1.0","original_prompt":"Create a website for my startup.","intent":"Launch a business website","task":"Design a startup website","context":[],"constraints":[],"output_requirements":[],"ambiguities":[],"missing_information":[],"optimization_opportunities":[],"optimized_prompt":"Create a polished website brief for a startup with a clear call to action."}'
    analyzer = PromptAnalyzer(FakeProvider(content))

    result = analyzer.analyze("Create a website for my startup.")

    assert result.original_prompt == "Create a website for my startup."
    assert result.schema_version == "1.0"

def test_analyzer_rejects_empty_prompt():
    analyzer = PromptAnalyzer()

    with pytest.raises(ValueError):
        analyzer.analyze("")

def test_prompt_analysis_contract_preserves_original_prompt_and_empty_lists():
    analysis = PromptAnalysis.model_validate(
        {
            "schema_version": "1.0",
            "original_prompt": "  Build a landing page for a bakery  ",
            "intent": "Promote a local bakery",
            "task": "Draft a landing page",
            "context": [],
            "constraints": [],
            "output_requirements": [],
            "ambiguities": [],
            "missing_information": [],
            "optimization_opportunities": [],
            "optimized_prompt": "Design a bakery landing page for local customers.",
        }
    )

    assert analysis.original_prompt == "  Build a landing page for a bakery  "
    assert analysis.context == []
    assert analysis.schema_version == "1.0"


def test_prompt_analysis_rejects_missing_fields_and_extra_fields():
    with pytest.raises(ValidationError):
        PromptAnalysis.model_validate(
            {
                "original_prompt": "Draft a blog post",
                "intent": "Write a blog post",
                "task": "Write a blog post",
                "context": [],
                "constraints": [],
                "output_requirements": [],
                "ambiguities": [],
                "missing_information": [],
                "optimization_opportunities": [],
                "optimized_prompt": "Write a blog post in a friendly tone.",
                "unexpected_field": "not allowed",
            }
        )

    with pytest.raises(ValidationError):
        PromptAnalysis.model_validate(
            {
                "schema_version": "1.0",
                "original_prompt": "Draft a blog post",
                "intent": "Write a blog post",
                "task": "Write a blog post",
                "context": ["valid", 3],
                "constraints": [],
                "output_requirements": [],
                "ambiguities": [],
                "missing_information": [],
                "optimization_opportunities": [],
                "optimized_prompt": "Write a blog post in a friendly tone.",
            }
        )


def test_evaluator_validates_all_list_items_are_strings():
    analysis = PromptAnalysis(
        schema_version="1.0",
        original_prompt="Explain machine learning",
        intent="Understand machine learning",
        task="Explain machine learning",
        context=["intro"],
        constraints=["Keep it beginner-friendly"],
        output_requirements=["Simple explanation"],
        ambiguities=[],
        missing_information=[],
        optimization_opportunities=[],
        optimized_prompt="Explain machine learning in clear beginner-friendly terms.",
    )

    assert evaluate_analysis(analysis).valid is True

    analysis.context = ["valid", 123]  # type: ignore[list-item]

    result = evaluate_analysis(analysis)

    assert result.valid is False
    assert any("context" in error for error in result.errors)

def test_analyzer_rejects_whitespace_prompt():
    analyzer = PromptAnalyzer()

    with pytest.raises(ValueError):
        analyzer.analyze("   ")