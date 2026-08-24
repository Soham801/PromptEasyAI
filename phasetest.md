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

## Phase 8: Prompt Optimization Core Hardening - Completed

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_analyzer.py tests/test_evaluator.py tests/test_provider.py tests/test_cli.py tests/test_backend.py
```

Expected result:

```text
31 passed in 1.55s
```

This verifies the provider-agnostic optimizer contract, intent-related output validation, preservation of explicit requirements, no-fabrication checks, and the offline-safe service/API workflow.

## Phase 9: Production Readiness And Security - Completed

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m prompteasy.cli demo --text "Explain machine learning to a beginner"
```

Expected output includes:

```text
PromptEasyAI Verification
Original prompt: Explain machine learning to a beginner
Optimized prompt: Explain machine learning to a beginner. Provide a clear, direct, and well-structured response.
Validation: PASS
```

This verifies the completed Phase 9 V0.1 operational baseline: a user can inspect the complete offline analysis, optimization, and validation workflow directly from the terminal.

The local interface launch check is:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m uvicorn prompteasy.service:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` and confirm the PromptEasyAI interface loads. Confirm `http://127.0.0.1:8000/health` returns service status metadata. Stop the server with `Ctrl+C` after verification.

The backend production-baseline checks are:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_backend.py
```

Expected result:

```text
9 passed
```

These checks cover request IDs, health metadata, request metrics, bounded request protection, and clean invalid-input responses.

## Phase 10: Interface Polish And User Workflow - In Progress

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_backend.py
```

Expected result:

```text
9 passed
```

This verifies the polished UI contract, including editable optimized output, visible validation status, accessible live output, and backend compatibility. Browser-level desktop/mobile automation remains the final Phase 10 task.
