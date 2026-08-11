from .models import PromptAnalysis

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