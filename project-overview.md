# Project Overview

## Product summary
PromptEasyAI is a prompt-quality assistant for turning vague or incomplete user prompts into clearer, more effective instructions for downstream LLMs. It helps a user understand the original prompt, identify missing information, surface ambiguities, preserve constraints, and generate a stronger optimized prompt without inventing facts.

The end goal is a polished product that supports a simple workflow:

1. User enters a prompt.
2. The system analyzes intent, task, context, constraints, output needs, ambiguities, and missing information.
3. The system produces a stronger optimized prompt.
4. The user reviews, edits, copies, saves, exports, or reuses the result.
5. History and personalization settings make future prompt improvement faster and more tailored.

## What the project already includes
The repository currently contains a working Python package with the following implemented pieces:

- Strict `PromptAnalysis` contract with versioned structured output
- Pydantic validation for required fields and list content
- Offline provider for local testing and deterministic behavior
- Groq provider abstraction with provider error normalization
- CLI for analyze/evaluate/config actions
- FastAPI backend with health, config, analysis, evaluation, history, and preferences endpoints
- Browser-based UI shell for prompt entry and analysis results
- Automated tests covering analyzer behavior, provider behavior, CLI behavior, backend API behavior, and UI workflow basics

## Core product idea
The product is not meant to answer the user's task. It is meant to improve the prompt used to send the task to another model.

This means the system should:

- preserve the user's intent
- separate explicit requirements from assumptions
- highlight missing information instead of guessing
- surface ambiguities rather than hiding them
- produce a downstream prompt that is ready for reuse

## End goal
The end goal is a usable product that feels like a prompt improvement workspace for real users.

A full end-state product would include:

- a polished web interface for prompt authoring and analysis
- copy/export/save actions
- prompt history and version tracking
- personalization preferences such as tone, audience, and domain
- reliable API behavior with offline-safe testing
- production-ready operational practices and deployment readiness

## Current maturity
The project has already reached the main product milestones through Phase 7 in the delivery plan, including:

- Phase 1: structured prompt-analysis contract
- Phase 2: provider reliability layer
- Phase 3: evaluation and quality measurement
- Phase 4: public Python API and CLI
- Phase 5: backend API service
- Phase 6: user interface
- Phase 7: persistence and personalization

The product is now positioned as a real prompt-improvement tool rather than a prototype library.

## Project direction
The recommended next direction is to continue following the planned roadmap:

- further harden the UI experience
- improve stored history and personalization features
- expand evaluation quality scoring
- prepare for production readiness and security review

## Success criteria
The project is successful when:

- a user can enter a prompt and receive a clear optimized version
- the prompt is validated and safe to reuse
- the workflow is easy to understand in the UI and CLI
- the app works without requiring external network access for default validation
- the system supports reuse, exploration, and iterative improvement over time
