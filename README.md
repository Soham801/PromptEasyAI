# PromptEasyAI

PromptEasyAI analyzes a user's raw prompt and produces a clearer, more effective version for use with another large language model. It identifies the user's intent, task, context, constraints, output requirements, ambiguities, and missing information before returning a ready-to-use optimized prompt.

The project currently includes a Python library, CLI, and FastAPI web interface. Groq provides the live language model backend, while the offline provider makes local verification deterministic and network-free.

## Objective

PromptEasyAI is designed to improve the quality and reliability of downstream LLM results by helping users turn underspecified prompts into precise instructions without changing their original intent.

The analyzer must:

- Preserve the original prompt exactly.
- Distinguish explicit requirements from inferred or missing information.
- Identify ambiguity instead of silently guessing.
- Preserve the user's constraints and requested output format.
- Produce an optimized prompt, not the answer to the user's request.

## Current Status

### Phase 9: Production Readiness Baseline - Complete

- Groq-backed prompt analysis.
- Strict JSON Schema response format.
- Pydantic validation through `PromptAnalysis`.
- Ten-field analysis contract.
- Optimized prompt returned in the same response.
- Provider-agnostic optimization with intent and no-fabrication validation.
- Human-readable `demo` CLI verification command.
- FastAPI health metadata, request IDs, metrics, rate limiting, and clean validation errors.
- Offline-safe automated test suite.

### Phase 10: Interface Polish - Complete

- Improve responsive layout, accessibility, comparison, editing, and browser-level coverage.
- Preserve the existing FastAPI contract while making the interface ready for repeated user workflows.
- The optimized prompt is editable, visibly validated, and used by copy/export actions.

### Phase 11B: Adaptive Optimization - Complete

- Deterministic question-first, constraint-first, format-first, reasoning-first, and direct strategies.
- Optional audience, tone, and domain conditioning.
- Offline-safe clarification fallback for high-impact missing information.

### Phase 12: Quality Benchmark And Release Gates - Complete

- Versioned benchmark coverage for vague, adversarial, domain-heavy, and format-critical prompts.
- Machine-readable quality metrics and a release-gate CLI command.
- Current offline baseline: 10/10 cases passed with zero hallucination risk.
- Provider/model comparison CLI with persisted JSON reports.
- CI quality workflow enforcing benchmark and test gates.

### Next: Phase 13 Public Deployment

- Review benchmark artifacts across one release cycle.
- Add authentication, persistent storage, secret management, HTTPS deployment, monitoring, quotas, and rollback procedures.

See [ProjectDetails.md](ProjectDetails.md) for the canonical product definition and [plan.md](plan.md) for the delivery roadmap.

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

Or install the package and its declared dependencies into the existing virtual environment:

```powershell
.\.venv\Scripts\python -m pip install -e .
```

Create a `.env` file in the repository root:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env` or expose the API key in source code.

## Command-Line Usage

## Run The Web Interface

From the repository root, start the local FastAPI server:

```powershell
.\.venv\Scripts\python -m uvicorn prompteasy.service:app --reload
```

Provider selection for CLI and web flows is controlled with environment variables:

```powershell
$env:PROMPTEASY_PROVIDER="offline"  # default, deterministic local behavior
```

To use Groq-backed optimization quality instead of offline deterministic behavior:

```powershell
$env:PROMPTEASY_PROVIDER="groq"
$env:PROMPTEASY_MODEL="openai/gpt-oss-20b"
```

When `PROMPTEASY_PROVIDER` is set to `groq`, ensure `GROQ_API_KEY` is present in `.env`.

Open http://127.0.0.1:8000 in a browser. Enter a prompt, select **Analyze**, edit the optimized prompt if needed, then use **Copy optimized prompt** or **Export JSON**. The current web UI uses the deterministic offline provider, so it works without an API key.

Useful service endpoints:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/api/metrics

Stop the server with `Ctrl+C`.

Run the interactive CLI:

```powershell
uv run python main.py
```

Enter a prompt when requested. The CLI prints the original prompt, its structured analysis, optimization opportunities, and the optimized prompt.

For a deterministic, human-readable verification output without network access:

```powershell
.\.venv\Scripts\python -m prompteasy.cli demo --text "Explain machine learning to a beginner"
```

This displays the detected intent, task, ambiguities, missing information, optimized prompt, and final validation status.

## Use The Live Groq Model

The interactive CLI uses `GroqProvider` and requires `GROQ_API_KEY` in `.env`:

```powershell
.\.venv\Scripts\python main.py
```

For a library call with an explicit model:

```python
from prompteasy import PromptAnalyzer
from prompteasy.llm import GroqProvider

provider = GroqProvider(model="openai/gpt-oss-20b")
analysis = PromptAnalyzer(provider=provider).analyze(
	"Create a concise onboarding guide for a new Python developer."
)
print(analysis.optimized_prompt)
```

Live provider probes are intentionally excluded from the default test suite. Run them only when credentials and network access are available.

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

This evaluator checks required fields, semantic relation, explicit requirement preservation, and unsupported details in optimized prompts.

Run the offline benchmark and release gate:

```powershell
.\.venv\Scripts\python -m prompteasy.cli benchmark
```

The current gate requires a pass rate of at least `0.80` and zero detected hallucination risk. The command emits machine-readable JSON and returns a nonzero exit code when the gate fails.

Compare provider/model configurations and persist the report:

```powershell
.\.venv\Scripts\python -m prompteasy.cli benchmark `
	--compare offline:baseline `
	--compare offline:candidate `
	--output reports/benchmark-comparison.json
```

The CI workflow runs this offline comparison and uploads the JSON report as an artifact. Groq comparisons are opt-in and require `GROQ_API_KEY` and network access.

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
	evaluator.py              Quality and no-fabrication validation
  llm.py                   Groq provider and environment configuration
  models.py                Pydantic response models
	optimizer.py             Provider-agnostic optimization contract
	service.py               FastAPI API and web interface
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
