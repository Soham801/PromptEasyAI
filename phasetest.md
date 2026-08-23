# Phase Test Guide

This file documents the exact commands used to validate each completed phase in this project.

## Phase 1: Core Prompt Analysis Contract

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_analyzer.py tests/test_evaluator.py
```

Expected result:

```text
9 passed in 1.13s
```

This verifies the versioned PromptAnalysis contract, strict validation of required fields and list contents, and the deterministic non-network test coverage for the prompt-analysis phase.

## Phase 2: LLM Provider And Reliability Layer

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_analyzer.py tests/test_evaluator.py tests/test_provider.py
```

Expected result:

```text
12 passed in 1.72s
```

This verifies the provider abstraction, offline/mock provider flow, provider error normalization, API key guard, and bounded retry behavior for retryable failures.

## Phase 3: Evaluation And Quality Measurement

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_analyzer.py tests/test_evaluator.py tests/test_provider.py
```

Expected result:

```text
16 passed in 1.86s
```

This verifies structural evaluation, semantic evaluation, evaluation dataset coverage, and pass-rate reporting for the quality-measurement phase.

## Phase 4: Public Python API And CLI

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_analyzer.py tests/test_evaluator.py tests/test_provider.py tests/test_cli.py
```

Expected result:

```text
20 passed in 1.77s
```

This verifies the stable Python API surface, JSON-serializable analysis output, evaluation helper functions, and the command-line interface for analyze/evaluate/config actions.
