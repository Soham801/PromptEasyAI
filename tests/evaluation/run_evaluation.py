from prompteasy.analyzer import PromptAnalyzer
from prompteasy.evaluator import evaluate_analysis

from .prompts import EVALUATION_PROMPTS

def main():
    analyzer = PromptAnalyzer()

    total = len(EVALUATION_PROMPTS)
    passed = 0

    for item in EVALUATION_PROMPTS:

        print(f"\n{'=' * 60}")
        print(f"Prompt: {item.name}")
        print(f"Difficulty: {item.difficulty}")
        print(f"Input: {item.prompt}")

        analysis = analyzer.analyze(item.prompt)

        result = evaluate_analysis(analysis)