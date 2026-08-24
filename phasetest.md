# Phase Test Guide

This file documents the exact commands used to validate each completed phase in this project.

> Note: the live Groq structured-output probe is now an opt-in integration test. It is skipped by default and only runs when `PROMPTEASY_RUN_LIVE_GROQ=1` is set, keeping the normal suite deterministic and offline-safe.

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

## Phase 5: Backend Service

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_analyzer.py tests/test_evaluator.py tests/test_provider.py tests/test_cli.py tests/test_backend.py
```

Expected result:

```text
24 passed in 3.63s
```

This verifies the health check, analysis endpoint, evaluation endpoint, config endpoint, and HTTP contract for the backend service layer.

## Phase 6: User Interface

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_backend.py tests/test_analyzer.py tests/test_evaluator.py tests/test_provider.py tests/test_cli.py
```

Expected result:

```text
25 passed in 2.11s
```

This verifies the FastAPI-served UI shell, the analysis workflow, copy/reset/export controls, and the offline-safe test suite for the user-facing phase.

## Phase 7: Persistence And Personalization

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_backend.py tests/test_analyzer.py tests/test_evaluator.py tests/test_provider.py tests/test_cli.py
```

Expected result:

```text
27 passed in 2.31s
```

This verifies the in-memory history API, saved prompt entries, and personalization preferences that support user retention and style customization.

## Phase 8: Prompt Optimization Core Hardening

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_analyzer.py tests/test_evaluator.py tests/test_provider.py tests/test_cli.py tests/test_backend.py
```

Expected result:

```text
27 passed in 2.12s
```

This is the next milestone and focuses on optimizer hardening, intent-preservation validation, and no-fabrication checks to match the V0.1 product definition.
