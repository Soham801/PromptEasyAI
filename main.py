from prompteasy import PromptAnalyzer

def main():
    analyzer = PromptAnalyzer()

    prompt = input("Enter your prompt: ")

    analysis = analyzer.analyze(prompt)

    print("\n Prompt Analysis")
    print("=" * 50)

    print(f"Original Prompt:{analysis.original_prompt}")
    print(f"Intent: {analysis.intent}")
    print(f"Task: {analysis.task}")
    print(f"Context: {analysis.context}")
    print(f"Constraints: {analysis.constraints}")
    print(f"Output Requirements: {analysis.output_requirements}")
    print(f"Ambiguities: {analysis.ambiguities}")
    print(f"Missing Information: {analysis.missing_information}")
    print(f"Optimization Opportunities: {analysis.optimization_opportunities}")
    print(f"Optimized Prompt: {analysis.optimized_prompt}")

if __name__ == "__main__":
    main()
