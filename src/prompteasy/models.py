from pydantic import BaseModel , Field

class PromptAnalysis(BaseModel):
    """
    Structured representation of a user's prompt.
    """

    original_prompt: str = Field(
        description = "The exact prompt provided by the user."
    )

    intent: str = Field(
        description="The primary goal the user is trying to acomplish."
    )

    task: str = Field(
        description= "The specific task the LLM is being asked to perform."
    )
    context: list[str] = Field(
        default_factory=list,
        description= "Relevant context explicitly provided by the user"
    )
    constraints: list[str] = Field(
        default_factory=list,
        description = "Explicit constraints or restrictions in the prompt."
    )
    output_requirements: list[str] = Field(
        default_factory=list,
        description="Requirements describing the desired output."
    )
    ambiguities:list[str] = Field(
        default_factory=list,
        description="Parts of the prompt that are vague or open to multiple interpretations."
    )
    missing_information:list[str] = Field(
        default_factory=list,
        description="Information that could materially improve execution of the task."
    )
    optimization_oppotunities: list[str] = Field(
        default_factory=list,
        description="Potential ways the prompt could be improved without changing the intent"
    )