from prompteasy.evaluator import evaluate_analysis
from prompteasy.models import PromptAnalysis

def test_valid_prompt_analysis():

    analysis = PromptAnalysis(
        original_prompt="Explain machine learning",
        intent="Understand machine learning",
        task="Explain machine learning",
        context=[],
        constraints=[],
        output_requirements=[],
        ambiguities=[],
        missing_information=[],
        optimization_oppotunities=[],
    )

    result = evaluate_analysis(analysis)

    assert result.valid is True
    assert result.errors == []


def test_empty_original_prompt_is_invalid():

    analysis = PromptAnalysis(
        original_prompt="",
        intent="Understand machine learning",
        task="Explain machine learning",
        context=[],
        constraints=[],
        output_requirements=[],
        ambiguities=[],
        missing_information=[],
        optimization_oppotunities=[],
    )

    result = evaluate_analysis(analysis)

    assert result.valid is False
    assert "original_prompt is empty" in result.errors