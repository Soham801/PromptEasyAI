from dataclasses import dataclass

@dataclass(frozen=True)
class EvaluationPrompt:
    name: str
    prompt:str
    expected_intent: str
    expected_task: str
    difficulty: str


EVALUATION_PROMPTS = [
    EvaluationPrompt(
        name="simple_question",
        prompt="What is machine learning?",
        expected_intent="Learn about machine learning",
        expected_task="Explain machine learning",
        difficulty="easy",
    ),

    EvaluationPrompt(
        name="technical_explanation",
        prompt=(
            "Explain how transformers work in large language models. "
            "I understand basic neural networks but don't know attention. "
        ),
        expected_intent="Understand how transformers work in LLMs",
        expected_task="Explain transformer architecture and attention",
        difficulty="medium"
    ),

    EvaluationPrompt(
        name="",
        prompt="",
    )
]