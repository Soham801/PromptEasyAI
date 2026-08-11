import pytest 

from prompteasy import PromptAnalyzer

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