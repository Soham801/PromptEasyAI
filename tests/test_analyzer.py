from types import SimpleNamespace

import pytest

from prompteasy import PromptAnalyzer


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
    content = '{"original_prompt":"Explain ML","intent":"Learn ML","task":"Explain machine learning","context":[],"constraints":[],"output_requirements":[],"ambiguities":[],"missing_information":[],"optimization_opportunities":["Specify the audience"],"optimized_prompt":"Explain machine learning to a beginner using one practical example."}'

    result = PromptAnalyzer(FakeProvider(content)).analyze("Explain ML")

    assert result.original_prompt == "Explain ML"
    assert result.optimized_prompt.startswith("Explain machine learning")

def test_analyzer_accepts_valid_prompt():
    analyzer = PromptAnalyzer()

    result = analyzer.analyze("Create a website for my startup.")

    assert result.original_prompt == "Create a website for my startup."

def test_analyzer_rejects_empty_prompt():
    analyzer = PromptAnalyzer()

    with pytest.raises(ValueError):
        analyzer.analyze("")


def test_analyzer_rejects_whitespace_prompt():
    analyzer = PromptAnalyzer()

    with pytest.raises(ValueError):
        analyzer.analyze("   ")