from __future__ import annotations
from typing import Final
from groq import BadRequestError
from .llm import GroqProvider
from .models import PromptAnalysis


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_ANALYSIS_ATTEMPTS: Final[int] = 2

ANALYSIS_SCHEMA_NAME: Final[str] = "prompt_analysis"


# ---------------------------------------------------------------------------
# Prompt Analyzer
# ---------------------------------------------------------------------------

class PromptAnalyzer:
    """
    Analyzes a raw user prompt and converts it into a structured
    PromptAnalysis representation.

    The analyzer is intentionally separate from the prompt optimizer.
    Its responsibility is to understand and represent the user's
    original request without executing or rewriting it.
    """

    def __init__(self, provider: GroqProvider | None = None) -> None:
        """
        Initialize the prompt analyzer.

        Args:
            provider: Optional GroqProvider instance. If omitted,
                a default GroqProvider is created.
        """
        self.provider = provider or GroqProvider()

        # Generate the schema once during initialization instead of
        # regenerating it for every analysis attempt.
        self._schema = PromptAnalysis.model_json_schema()

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def analyze(self, prompt: str) -> PromptAnalysis:
        """
        Analyze a raw user prompt.

        Args:
            prompt: Raw prompt supplied by the user.

        Returns:
            A validated PromptAnalysis instance.

        Raises:
            ValueError: If the prompt is empty or contains only whitespace.
            RuntimeError: If structured analysis fails after all attempts.
        """

        if not isinstance(prompt, str):
            raise TypeError("Prompt must be a string.")

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        last_error: Exception | None = None

        for attempt in range(1, MAX_ANALYSIS_ATTEMPTS + 1):
            try:
                system_instruction = self._build_system_instruction(attempt)

                response = self.provider.client.chat.completions.create(
                    model=self.provider.model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_instruction,
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": ANALYSIS_SCHEMA_NAME,
                            "strict": True,
                            "schema": self._schema,
                        },
                    },
                )

                content = response.choices[0].message.content

                if not content or not content.strip():
                    raise RuntimeError(
                        "The LLM returned an empty response."
                    )

                # Pydantic performs the final application-level
                # validation after Groq's schema validation.
                return PromptAnalysis.model_validate_json(content)

            except BadRequestError as exc:
                """
                Groq can occasionally reject a structured generation even
                when the schema itself is valid. Retry once with a reinforced
                instruction before failing.
                """
                last_error = exc

                if attempt < MAX_ANALYSIS_ATTEMPTS:
                    continue

                raise RuntimeError(
                    "Prompt analysis failed after "
                    f"{MAX_ANALYSIS_ATTEMPTS} attempts because Groq "
                    "could not generate schema-compliant JSON."
                ) from exc

            except ValueError as exc:
                """
                Covers Pydantic validation failures and other value-related
                response problems.

                These are not silently retried because they may indicate
                a genuine schema/application issue.
                """
                raise RuntimeError(
                    "Prompt analysis produced an invalid structured response."
                ) from exc

            except RuntimeError:
                """
                Empty-response or explicit runtime failures are propagated.
                """
                raise

        # Defensive fallback. The loop should always either return or raise.
        raise RuntimeError(
            "Prompt analysis failed unexpectedly."
        ) from last_error

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _build_system_instruction(attempt: int) -> str:
        """
        Build the analyzer instruction.

        On retry, add a short reinforcement specifically targeting
        schema-completeness failures.
        """

        if attempt == 1:
            return ANALYZER_INSTRUCTION

        return f"""
{ANALYZER_INSTRUCTION}

RETRY REQUIREMENT:

This is a retry of the structured analysis.

Before completing your response, verify that ALL 10 required fields
are present:

1. original_prompt
2. intent
3. task
4. context
5. constraints
6. output_requirements
7. ambiguities
8. missing_information
9. optimization_opportunities
10. optimized_prompt

Every field is mandatory.

Every array field must contain an array.

If a category has no relevant information, return [].

Do not stop generation before all 9 fields are present.
"""


# ---------------------------------------------------------------------------
# Analyzer System Instruction
# ---------------------------------------------------------------------------

ANALYZER_INSTRUCTION: Final[str] = """
You are PromptEasy's Prompt Analyzer.

Your ONLY job is to analyze the user's raw prompt and return a
structured representation of that prompt.

Do NOT answer the user's request.

Do NOT execute the requested task.

Do NOT rewrite the user's prompt.

Do NOT optimize the user's prompt.

Analyze the request only.

The structured response contains exactly these 10 fields:

1. original_prompt
2. intent
3. task
4. context
5. constraints
6. output_requirements
7. ambiguities
8. missing_information
9. optimization_opportunities
10. optimized_prompt

Every field is mandatory.

For every array field, return an array.
If there is no relevant information, return [].

FIELD DEFINITIONS:

original_prompt:
The exact original prompt provided by the user.

intent:
The user's primary goal.

task:
The specific task the user wants an AI system to perform.

context:
Relevant contextual information explicitly provided by the user.

constraints:
Explicit restrictions, limitations, preferences, or requirements.

output_requirements:
Requested output format, structure, length, style, or content.

ambiguities:
Parts of the request that are genuinely vague, ambiguous,
or underspecified.

missing_information:
Information that would materially improve execution of the task.

optimization_opportunities:
Specific ways the prompt could be made clearer, more specific,
or more effective without changing the user's original intent.

optimized_prompt:
A complete, ready-to-use version of the user's prompt that improves
clarity and specificity without inventing facts, requirements, or context.

IMPORTANT RULES:

- Preserve the user's original intent.
- Preserve the original prompt exactly in original_prompt.
- Do not invent facts, requirements, or context.
- Do not perform the task requested by the user.
- Do not generate the output requested by the user.
- The user's requested output format must be analyzed under
  output_requirements rather than produced.
- Distinguish genuine ambiguity from information that is simply
  unnecessary.
- Missing information should only include information that would
  materially improve execution.
- Optimization opportunities should describe improvements to the
  prompt, not perform those improvements.
- optimized_prompt must be a prompt for the requested task, not the
    answer to that task.
- Preserve all explicit requirements and constraints in optimized_prompt.
- Resolve ambiguity only by making the uncertainty explicit or by using
    a clearly marked placeholder; do not guess missing facts.
- Do not omit any field.
- optimization_opportunities MUST always be present.
- optimized_prompt MUST always be present.
- If there are no useful optimization opportunities, return [].
- Keep the analysis concise but sufficiently specific.

Analyze the user's prompt only.
"""