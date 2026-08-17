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

        if result.valid:
            passed += 1
            print("Structural validation: PASS")
        else:
            print("Structural validation: FAIL")
            for error in result.errors:
                print(f" - {error}")

        print(f"Intent: {analysis.intent}")
        print(f"Task: {analysis.task}")

    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{total} structurally valid")


if __name__ == "__main__":
    main()