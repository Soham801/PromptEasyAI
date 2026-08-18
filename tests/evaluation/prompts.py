from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationPrompt:
    name: str
    prompt: str
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
            "I understand basic neural networks but don't know attention."
        ),
        expected_intent="Understand how transformers work in LLMs",
        expected_task="Explain transformer architecture and attention",
        difficulty="medium",
    ),

    EvaluationPrompt(
        name="coding_request",
        prompt=(
            "Write a Python function that takes a list of numbers "
            "and returns the second largest number."
        ),
        expected_intent="Obtain a Python solution for finding the second largest number",
        expected_task="Write a Python function",
        difficulty="easy",
    ),

    EvaluationPrompt(
        name="ambiguous_request",
        prompt="Make my project better.",
        expected_intent="Improve the user's project",
        expected_task="Improve a project",
        difficulty="hard",
    ),

    EvaluationPrompt(
        name="multiple_constraints",
        prompt=(
            "Explain RAG to me in simple terms. "
            "Keep it under 300 words, use a real-world example, "
            "and don't use mathematical notation."
        ),
        expected_intent="Understand RAG",
        expected_task="Explain retrieval-augmented generation",
        difficulty="medium",
    ),

    EvaluationPrompt(
        name="structured_output",
        prompt=(
            "Compare PostgreSQL and MongoDB for an AI application. "
            "Give me a table containing scalability, flexibility, "
            "query capabilities, and typical use cases."
        ),
        expected_intent="Compare PostgreSQL and MongoDB for an AI application",
        expected_task="Compare two databases",
        difficulty="medium",
    ),

    EvaluationPrompt(
        name="role_based_request",
        prompt=(
            "Act as a senior Python developer and review this code "
            "for performance problems and possible bugs."
        ),
        expected_intent="Get an expert code review",
        expected_task="Review Python code",
        difficulty="medium",
    ),

    EvaluationPrompt(
        name="incomplete_prompt",
        prompt="Build an AI app for me.",
        expected_intent="Build an AI application",
        expected_task="Design or build an AI application",
        difficulty="hard",
    ),

    EvaluationPrompt(
        name="long_prompt",
        prompt=(
            "I am building a document question answering system using "
            "Python, FastAPI, Qdrant and an embedding model. Users will "
            "upload multiple PDFs and ask questions about them. I want "
            "the system to retrieve relevant chunks, generate an answer "
            "using an LLM, and cite the source documents. Explain how "
            "I should architect this system and what components I need."
        ),
        expected_intent="Design a document question answering system",
        expected_task="Provide a system architecture and required components",
        difficulty="hard",
    ),
]