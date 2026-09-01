from types import SimpleNamespace

import pytest

from prompteasy.models import PromptAnalysis
from prompteasy.llm import build_offline_optimized_prompt
from prompteasy.evaluator import accuracy_score, quality_delta
from prompteasy.optimizer import (
    OptimizationPreferences,
    ProviderPromptOptimizer,
    select_optimization_strategy,
)


class FakeOptimizerProvider:
    model = "test-model"

    def __init__(self, content):
        self.content = content
        self.last_request = None

    def generate(self, *, model, messages, response_format=None):
        self.last_request = {
            "model": model,
            "messages": messages,
            "response_format": response_format,
        }
        return SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content=self.content))
            ]
        )


class RetryOptimizerProvider(FakeOptimizerProvider):
    def __init__(self, contents):
        super().__init__(contents[0])
        self.contents = iter(contents)

    def generate(self, *, model, messages, response_format=None):
        self.last_request = {"model": model, "messages": messages, "response_format": response_format}
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=next(self.contents)))]
        )


def build_analysis(**overrides):
    values = {
        "schema_version": "1.0",
        "original_prompt": "Explain caching to a beginner.",
        "intent": "Understand caching",
        "task": "Explain caching",
        "context": [],
        "constraints": [],
        "output_requirements": ["Use a simple explanation"],
        "ambiguities": [],
        "missing_information": [],
        "optimization_opportunities": [],
        "optimized_prompt": "Explain caching to a beginner using simple language.",
    }
    values.update(overrides)
    return PromptAnalysis(**values)


def test_provider_optimizer_returns_validated_prompt():
    provider = FakeOptimizerProvider(
        "Explain caching to a beginner using simple language and one analogy."
    )

    result = ProviderPromptOptimizer(provider).optimize(build_analysis())

    assert result.startswith("Explain caching")
    assert provider.last_request["response_format"] is None
    assert provider.last_request["messages"][0]["role"] == "system"


def test_provider_optimizer_rejects_fabricated_detail():
    provider = FakeOptimizerProvider(
        "Explain caching to a beginner in exactly 12 detailed sections."
    )

    with pytest.raises(ValueError, match="unsupported numeric"):
        ProviderPromptOptimizer(provider).optimize(build_analysis())


def test_provider_optimizer_retries_with_tightened_constraints():
    provider = RetryOptimizerProvider(
        [
            "Explain caching in exactly 12 sections.",
            "Explain caching to a beginner using simple language and one analogy.",
        ]
    )

    result = ProviderPromptOptimizer(provider).optimize(build_analysis())

    assert result.startswith("Explain caching")
    assert "previous candidate failed validation" in provider.last_request["messages"][0]["content"]


def test_optimizer_conditions_instruction_with_preferences():
    provider = FakeOptimizerProvider(
        "Explain caching to a beginner using simple language and one analogy."
    )

    ProviderPromptOptimizer(
        provider,
        preferences=OptimizationPreferences(
            tone="friendly",
            audience="new developers",
            domain="web performance",
        ),
    ).optimize(build_analysis(output_requirements=[]))

    instruction = provider.last_request["messages"][0]["content"]
    assert "Use audience: new developers." in instruction
    assert "Use tone: friendly." in instruction
    assert "Use domain: web performance." in instruction
    assert "Use direct optimization" in instruction


def test_optimizer_selects_question_first_for_high_impact_missing_information():
    analysis = build_analysis(
        missing_information=["Target audience.", "Preferred output format."]
    )

    assert select_optimization_strategy(analysis) == "question-first"


def test_optimizer_selects_other_adaptive_modes_deterministically():
    assert select_optimization_strategy(build_analysis(constraints=["Use JSON"])) == "constraint-first"
    assert select_optimization_strategy(build_analysis()) == "format-first"
    assert select_optimization_strategy(build_analysis(output_requirements=[])) == "direct"
    assert (
        select_optimization_strategy(
            build_analysis(output_requirements=[], task="Analyze the tradeoffs")
        )
        == "reasoning-first"
    )


def test_offline_question_first_prompt_asks_before_assuming():
    result = build_offline_optimized_prompt(
        "Original prompt:\nWrite an application for me.\n\n"
        "Use question-first mode: ask for the highest-impact missing details."
    )

    assert result.startswith("Write an application for me.")
    assert "ask for the missing details" in result
    assert "Do not assume answers" in result


def test_offline_prompt_compiler_builds_structured_ready_to_send_prompt():
    result = build_offline_optimized_prompt("Build a login page for a SaaS product")

    assert "Objective:" in result
    assert "Requirements:" in result
    assert "Acceptance criteria:" in result
    assert "SaaS" in result
    assert "web application" in result.lower()


def test_quality_delta_reports_improvement_and_requirement_coverage():
    analysis = build_analysis(
        constraints=["Do not use jargon"],
        optimized_prompt="Explain caching to a beginner using simple language. Do not use jargon.",
    )
    delta = quality_delta(analysis)

    assert delta.materially_improved is True
    assert delta.requirement_coverage == 1.0
    assert delta.optimized_tokens >= delta.original_tokens


def test_accuracy_score_reports_complete_quality_model():
    analysis = build_analysis(
        constraints=["Do not use jargon"],
        output_requirements=["Use a simple explanation", "Return 3 bullet points"],
        optimized_prompt="Explain caching to a beginner using simple language and three short bullet points. Do not use jargon.",
    )
    score = accuracy_score(analysis)

    assert 0.0 <= score.overall <= 1.0
    assert score.valid is True
    assert score.requirement_retention >= 0.8
    assert score.unsupported_claim_risk == 0.0
    assert score.confidence > 0.5


def test_task_classifier_matches_common_prompt_families():
    from prompteasy.task_classifier import classify_task_family

    assert classify_task_family("Build a login page for a SaaS product") == "build_implement"
    assert classify_task_family("Compare React and Vue for a dashboard") == "compare_choose"
    assert classify_task_family("Explain caching to a beginner") == "analyze_evaluate"


def test_prompt_spec_is_exported_from_package_root():
    import prompteasy

    assert hasattr(prompteasy, "PromptSpec")
    assert hasattr(prompteasy, "build_prompt_spec")
    assert hasattr(prompteasy, "render_prompt_spec")
