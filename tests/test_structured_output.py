__test__ = False

from prompteasy.llm import GroqProvider
from prompteasy.models import PromptAnalysis

provider = GroqProvider()

response = provider.client.chat.completions.create(
    model=provider.model,
    messages=[
        {
            "role": "system",
            "content": """
Analyze the user's prompt.

Do not answer the prompt.
Do not execute the requested task.

Return a structured analysis of the prompt.

If a category contains no information, return an empty array.
"""
        },
        {
            "role": "user",
            "content": """
Compare PostgreSQL and MongoDB for an AI application.
Give me a table containing scalability, flexibility,
query capabilities, and typical use cases.
"""
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "prompt_analysis",
            "strict": True,
            "schema": PromptAnalysis.model_json_schema(),
        }
    },
)

print(response.choices[0].message.content)