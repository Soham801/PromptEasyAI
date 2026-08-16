from prompteasy.evaluator import evaluate_analysis
from prompteasy.models import PromptAnalysis

def test_valid_prompt_analysis():

    analysis = PromptAnalysis(
        original_prompt="Explain machine learning",
        intent="Understand machine learning",
        task="Explain machine learning"
    )