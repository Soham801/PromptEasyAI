from types import SimpleNamespace

import pytest

from prompteasy.analyzer import PromptAnalyzer
from prompteasy.llm import GroqProvider, OfflineProvider, RateLimitError


def test_prompt_analyzer_accepts_offline_provider():
    provider = OfflineProvider(
        response=(
            '{"schema_version":"1.0","original_prompt":"Write a haiku",'
            '"intent":"Write a haiku","task":"Compose a haiku","context":[],'
            '"constraints":[],"output_requirements":[],"ambiguities":[],'
            '"missing_information":[],"optimization_opportunities":[],'
            '"optimized_prompt":"Write a haiku about the morning sky."}'
        )
    )

    result = PromptAnalyzer(provider).analyze("Write a haiku")

    assert result.original_prompt == "Write a haiku"
    assert result.schema_version == "1.0"


def test_groq_provider_requires_api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")

    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        GroqProvider()


def test_prompt_analyzer_retries_on_retryable_provider_errors():
    class FlakyProvider:
        def __init__(self):
            self.model = "test-model"
            self.calls = 0

        def generate(self, *, messages, response_format=None, model=None):
            self.calls += 1
            if self.calls == 1:
                raise RateLimitError("rate limited")

            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=(
                                '{"schema_version":"1.0","original_prompt":"Summarize the article",'
                                '"intent":"Summarize the article","task":"Summarize the article",'
                                '"context":[],"constraints":[],"output_requirements":[],'
                                '"ambiguities":[],"missing_information":[],'
                                '"optimization_opportunities":[],'
                                '"optimized_prompt":"Summarize the article in five bullet points."}'
                            )
                        )
                    )
                ]
            )

    provider = FlakyProvider()

    result = PromptAnalyzer(provider).analyze("Summarize the article")

    assert result.original_prompt == "Summarize the article"
    assert provider.calls == 2
