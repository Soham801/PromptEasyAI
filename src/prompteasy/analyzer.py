from .models import PromptAnalysis
from .llm import GroqProvider

class PromptAnalyzer:
    """
    Analyzes user prompt and converts them into 
    a structured PromptAnalysis representation.
    """

    def analyze(self,prompt:str) -> PromptAnalysis:
        """
        Analyze a user prompt.

        Args:
            prompt: Raw prompt supplied by the user.
        
        Returns:
            Structured PromptAnalysis.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        prompt = prompt.strip()

        return PromptAnalysis(
            original_prompt=prompt,
            intent="",
            task="",
            context=[],
            constraints=[],
            output_requirements=[],
            ambiguities=[],
            missing_information=[],
            optimization_oppotunities=[],
        )

ANALYZER_INSTRUCTION = """

You are the PromptEasy Prompt Analyzer.

Your job is to analyze a user's raw prompt and produce a structured
representation of what the user is trying to accomplish.

You are NOT the prompt optimizer.

Do not rewrite the user's prompt.

Do not answer the user's request.

Do not invent information that the user did not provide.

Your primary objective is to understand and accurately represent
the user's intent.

Analyze the prompt according to these dimensions:

1. Intent
Identify the user's primary goal.

2. Task
Identify the specific task the user wants the LLM to perform.

3. Context
Extract relevant contextual information explicitly provided
by the user.

4. Constraints
Extract explicit restrictions, limitations, preferences,
or requirements.

5. Output Requirements
Identify requirements concerning the desired output format,
structure, length, style, or content.

6. Ambiguities
Identify statements that could reasonably have multiple
interpretations or are too vague.

7. Missing Information
Identify information that would materially help an LLM
complete the task better.

8. Optimization Opportunities
Identify ways the prompt could become clearer, more specific,
or more effective without changing the user's intent.

Important rules:

- Preserve the user's original intent.
- Do not assume facts that are not present.
- Distinguish between information that is missing and information
  that is simply unnecessary.
- Do not criticize the user's request.
- Do not optimize the prompt yet.
- Be concise but sufficiently specific.


"""