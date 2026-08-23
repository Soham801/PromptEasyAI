from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PromptAnalysis(BaseModel):
    """
    Structured representation of a user's prompt.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = Field(
        description="Version of the public response contract.",
    )

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
        default_factory=list,
        description="Relevant context explicitly provided by the user.",
    )

    constraints: list[str] = Field(
        default_factory=list,
        description="Explicit constraints or restrictions in the prompt.",
    )

    output_requirements: list[str] = Field(
        default_factory=list,
        description="Requirements describing the desired output.",
    )

    ambiguities: list[str] = Field(
        default_factory=list,
        description="Parts of the prompt that are vague or open to multiple interpretations.",
    )

    missing_information: list[str] = Field(
        default_factory=list,
        description="Information that could materially improve execution of the task.",
    )

    optimization_opportunities: list[str] = Field(
        default_factory=list,
        description="Potential ways the prompt could be improved without changing the intent.",
    )

    optimized_prompt: str = Field(
        description="An improved version of the prompt that preserves the user's intent."
    )

    @field_validator(
        "original_prompt",
        "intent",
        "task",
        "optimized_prompt",
    )
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{info.field_name} must be a string.")
        if not value.strip():
            raise ValueError(f"{info.field_name} cannot be empty.")
        return value

    @field_validator(
        "context",
        "constraints",
        "output_requirements",
        "ambiguities",
        "missing_information",
        "optimization_opportunities",
    )
    @classmethod
    def validate_list_field(cls, value: list[str], info) -> list[str]:
        if not isinstance(value, list):
            raise TypeError(f"{info.field_name} must be a list of strings.")

        for index, item in enumerate(value):
            if not isinstance(item, str):
                raise TypeError(
                    f"{info.field_name} must contain only strings; item {index} is not a string."
                )
            if not item.strip():
                raise ValueError(
                    f"{info.field_name} contains an empty string at index {index}."
                )

        return value