from pydantic import BaseModel , Field

class PromptAnalysis(BaseModel):
    """
    Structured representation of a user's prompt.
    """

    original_prompt: str = Field(
        description = "The exact prompt provided by the user."
    )

    