from types import SimpleNamespace

import pytest

from prompteasy.models import PromptAnalysis
from prompteasy.optimizer import ProviderPromptOptimizer


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
