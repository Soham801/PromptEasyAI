# Phase Test Guide

This file documents the exact commands used to validate completed phases and the active Phase 12 quality gate.

> Note: live Groq probes are opt-in integration tests. They are skipped by default and only run when `PROMPTEASY_RUN_LIVE_GROQ=1` is set, keeping the normal suite deterministic and offline-safe.

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

## Phase 10: Interface Polish And User Workflow - Completed

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_backend.py
```

Expected result:

```text
9 passed
```

This verifies the polished UI contract, including editable optimized output, visible validation status, accessible live output, and backend compatibility.

Browser verification completed against the local Uvicorn server:

- Desktop viewport: `1440x900`, no horizontal overflow.
- Mobile viewport: `390x844`, no horizontal overflow.
- Interactive flow: entered a prompt, selected Analyze, and confirmed the rendered original prompt, semantic list output, editable optimized prompt, and validation badge.

## Phase 11A: Prompt Quality Recovery Sprint - Completed

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_optimizer.py tests/test_evaluator.py tests/test_cli.py
```

Expected result:

```text
22 passed
```

This verifies quality-delta signals, requirement coverage, ambiguity handling, over-compression protection, bounded retry with tightened constraints, and the shared public optimization flow.

## Phase 11B: Adaptive Optimization Engine - Completed

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_optimizer.py tests/test_backend.py
```

This verifies deterministic direct, question-first, constraint-first, format-first, and reasoning-first strategies, plus audience, tone, and domain conditioning.

## Phase 12: Quality Benchmark And Release Gates - Completed

Run the current offline benchmark gate:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m prompteasy.cli benchmark
```

Current verified result:

```text
10/10 cases passed
pass rate: 1.00
hallucination risk: 0.00
```

The gate requires a pass rate of at least `0.80` and zero hallucination risk.

Run the baseline/candidate comparison and persist the release artifact:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m prompteasy.cli benchmark --compare offline:baseline --compare offline:candidate --output reports/benchmark-comparison.json
```

The comparison records dataset version, provider, model, per-metric deltas, and gate status. The GitHub Actions workflow in `.github/workflows/quality.yml` runs the full offline suite, executes this comparison, and uploads the JSON report. Groq comparisons remain opt-in and require credentials and network access.

## Phase 13: Public Deployment And Operations - Next

Review benchmark artifacts across one release cycle before implementing production configuration, secret management, persistent storage, authentication, quotas, monitoring, rollback procedures, and security hardening.

## Phase 13A: Persistent Storage And Data Isolation - Completed

Run from the repository root:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_backend.py tests/test_config.py
```

Current verified result:

```text
13 passed
```

This verifies SQLite-backed history and preferences, storage schema initialization, optional bearer authentication, unauthorized persistence access rejection, and isolation of history records between user identities. Configure `PROMPTEASY_STORAGE_PATH` for the database file. Configure `PROMPTEASY_AUTH_TOKEN` to enable `Bearer <user-id>.<token>` authentication; the shared-token mechanism is intended as a controlled deployment boundary, not a complete public identity system.

## Full Offline Regression Suite

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q
```

Current result: `47 passed, 2 skipped`. The skipped tests are the opt-in live Groq probes.

## Phase 13: Public Deployment And Operations - In Progress

Configuration and container checks:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_backend.py
```

These checks verify offline development defaults, production rejection of the offline provider, rate-limit validation, and environment metadata in `/health`. Build the production image with:

```powershell
docker build -t prompteasyai:0.1.0 .
```

Remaining Phase 13 work is database migrations, managed secrets, full authentication and authorization, HTTPS, quotas, monitoring, rollback, vulnerability scanning, load testing, and prompt-injection validation.

## Phase 13B: Backup And Restore Operations - Completed

The storage layer now supports consistent SQLite backups and atomic restores through `Storage.backup_to()` and `Storage.restore_from()`. The implementation explicitly closes SQLite connections so replacement works on Windows, and rejects missing or same-path backup files.

Run the focused verification:

```powershell
cd C:\PromptEasyAI
.\.venv\Scripts\python -m pytest -q tests/test_cli.py tests/test_backend.py
```

Current verified result: `19 passed`.

Operators can use the maintenance CLI with the configured `PROMPTEASY_STORAGE_PATH`:

```powershell
.\.venv\Scripts\python -m prompteasy.cli storage --backup backups\prompteasy.db
.\.venv\Scripts\python -m prompteasy.cli storage --restore backups\prompteasy.db
```

Next Phase 13 steps are managed secrets, complete authentication and authorization, HTTPS deployment, quotas, monitoring and alerting, rollback procedures, vulnerability scanning, load testing, and prompt-injection validation.
