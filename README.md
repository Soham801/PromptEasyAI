# PromptEasyAI

PromptEasyAI analyzes a user's raw prompt and produces a clearer, more effective version for use with another large language model. It identifies the user's intent, task, context, constraints, output requirements, ambiguities, and missing information before returning a ready-to-use optimized prompt.

The project is currently a Python library with a command-line interface. Groq provides the language model backend, while Pydantic validates the structured response.

## Objective

PromptEasyAI is designed to improve the quality and reliability of downstream LLM results by helping users turn underspecified prompts into precise instructions without changing their original intent.

The analyzer must:

- Preserve the original prompt exactly.
- Distinguish explicit requirements from inferred or missing information.
- Identify ambiguity instead of silently guessing.
- Preserve the user's constraints and requested output format.
- Produce an optimized prompt, not the answer to the user's request.

## Current Status

### Phase 1: Structured Prompt Analysis - Complete

- Groq-backed prompt analysis.
- Strict JSON Schema response format.
- Pydantic validation through `PromptAnalysis`.
- Ten-field analysis contract.
- Optimized prompt returned in the same response.
- Basic structural evaluation with `EvaluationResult`.
- CLI demonstration through `main.py`.
- Mocked analyzer test coverage for the optimized prompt flow.

### Phase 2: Reliability And Evaluation - In Progress

- Expand mocked unit coverage for API failures, malformed responses, and retries.
- Separate live integration tests from the default test suite.
- Compare generated intent and task against semantic evaluation expectations.
- Strengthen validation for all list fields and optimized prompt quality.

### Phase 3: User Product - Planned

- Add a user-facing interface for entering, comparing, and copying prompts.
- Support configurable model and generation settings.
- Add prompt history and reusable analysis results.
- Provide feedback or scoring for clarity, completeness, and constraint preservation.

## How The System Works

```text
User prompt
	|
	v
PromptAnalyzer.analyze()
	|
	+--> Validate input is a non-empty string
	+--> Build the PromptAnalysis JSON Schema
	+--> Send system instructions and the prompt to Groq
	+--> Parse and validate the JSON response with Pydantic
	|
	v
PromptAnalysis
	|
	+--> Structured analysis fields
	+--> optimized_prompt for downstream LLM use
	+--> Optional evaluate_analysis() structural check
```

## Requirements

- Python 3.13 or newer.
- A Groq API key.
- Dependencies managed by `uv` or installed through the project metadata.

The default model is `openai/gpt-oss-20b`. It can be changed when constructing `GroqProvider` in library code.

## Installation

From the repository root:

```powershell
uv sync
```

Create a `.env` file in the repository root:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env` or expose the API key in source code.

## Command-Line Usage

Run the interactive CLI:

```powershell
uv run python main.py
```

Enter a prompt when requested. The CLI prints the original prompt, its structured analysis, optimization opportunities, and the optimized prompt.

## Library Usage

```python
from prompteasy import PromptAnalyzer

analyzer = PromptAnalyzer()
analysis = analyzer.analyze(
	"Explain retrieval augmented generation to me in simple terms."
)

print(analysis.optimized_prompt)
```

For a custom model configuration:

```python
from prompteasy.analyzer import PromptAnalyzer
from prompteasy.llm import GroqProvider

provider = GroqProvider(model="openai/gpt-oss-20b")
analyzer = PromptAnalyzer(provider=provider)
analysis = analyzer.analyze("Design an API for my application.")
```

## Response Contract

`PromptAnalyzer.analyze()` returns a `PromptAnalysis` object with these fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `original_prompt` | `str` | Exact user input. |
| `intent` | `str` | The user's primary goal. |
| `task` | `str` | The task requested from an LLM. |
| `context` | `list[str]` | Relevant context explicitly provided. |
| `constraints` | `list[str]` | Explicit restrictions and requirements. |
| `output_requirements` | `list[str]` | Requested format, style, length, or content. |
| `ambiguities` | `list[str]` | Vague or underspecified parts of the prompt. |
| `missing_information` | `list[str]` | Information that would materially improve execution. |
| `optimization_opportunities` | `list[str]` | Ways to improve clarity without changing intent. |
| `optimized_prompt` | `str` | Ready-to-use improved prompt. |

Additional fields are rejected by the Pydantic model to keep the LLM response contract explicit.

## Evaluation

The optional evaluator checks basic structural quality:

```python
from prompteasy.evaluator import evaluate_analysis

result = evaluate_analysis(analysis)

if result.valid:
	print("Analysis is structurally valid")
else:
	print(result.errors)
```

This evaluator currently checks required text fields and selected list fields. It does not yet measure semantic equivalence between the original and optimized prompts.

## Testing

Run the automated suite:

```powershell
uv run pytest -v
```

The default suite uses a fake provider for the optimized prompt unit test. The files `tests/test_groq.py` and `tests/test_structured_output.py` are manual live Groq probes and require network access and a valid API key; they are not collected as pytest test functions.

## Project Layout

```text
main.py                    Interactive CLI entry point
src/prompteasy/            Installable Python package
  analyzer.py              Groq request and structured response handling
  evaluator.py             Basic analysis validation
  llm.py                   Groq provider and environment configuration
  models.py                Pydantic response models
tests/                     Automated and manual test scripts
tests/evaluation/          Evaluation prompts and batch runner
pyproject.toml             Package metadata and tool configuration
```

## Design Principles

- Analysis and prompt improvement must preserve user intent.
- The analyzer should never execute the task it is analyzing.
- Structured output is validated at the application boundary.
- Missing information should be surfaced rather than fabricated.
- Deterministic unit tests should remain independent of external LLM services.
