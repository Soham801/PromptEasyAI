from pydantic import BaseModel, Field, ConfigDict

class PromptAnalysis(BaseModel):
    """
    Structured representation of a user's prompt.
    """

    model_config = ConfigDict(extra="forbid")

    original_prompt: str = Field(
        description="The exact prompt provided by the user."
    )

    intent: str = Field(
        description="The primary goal the user is trying to accomplish."
    )

    task: str = Field(
        description="The specific task the LLM is being asked to perform."
    )

    context: list[str] = Field(
        description="Relevant context explicitly provided by the user."
    )

    constraints: list[str] = Field(
        description="Explicit constraints or restrictions in the prompt."
    )

    output_requirements: list[str] = Field(
        description="Requirements describing the desired output."
    )

    ambiguities: list[str] = Field(
        description="Parts of the prompt that are vague or open to multiple interpretations."
    )

    missing_information: list[str] = Field(
        description="Information that could materially improve execution of the task."
    )

    optimization_opportunities: list[str] = Field(
        description="Potential ways the prompt could be improved without changing the intent."
    )

    optimized_prompt: str = Field(
        description="An improved version of the prompt that preserves the user's intent."
    )