# PromptEasyAI --- Project Details

> **Purpose of this document:** This file is the canonical
> project-context document for PromptEasyAI. It is written so that
> GitHub Copilot, developers, reviewers, and future contributors can
> understand what the project is, why it exists, how it works, what is
> currently being built, and what the long-term product is intended to
> become.
>
> **Current project phase:** Phase 1.5 --- active development\
> **Current baseline:** Restarted from a clean, explicitly tracked Phase
> 1.5 baseline on 2026-08-15\
> **Current core version target:** V0.1\
> **Primary principle:** Build a minimal, model-agnostic prompt
> optimization engine first. Do not prematurely build the full product.

------------------------------------------------------------------------

## 1. Project Overview

**PromptEasyAI** is an AI prompt optimization engine designed to
transform a user's raw, incomplete, vague, ambiguous, or poorly
structured prompt into a clearer, more specific, useful, and validated
prompt while preserving the user's original intent.

The fundamental idea is:

``` text
Raw User Prompt
      ↓
Prompt Understanding
      ↓
Intent Preservation
      ↓
Prompt Analysis
      ↓
Prompt Improvement
      ↓
Validation
      ↓
Optimized Prompt
```

PromptEasyAI is **not initially intended to be another general-purpose
chatbot**.

Its first responsibility is to improve the quality of a user's
instruction before that instruction is given to another AI model.

The system should be **model-agnostic**. The optimization engine should
not fundamentally depend on one specific LLM provider. A model such as
Groq-hosted models may be used during development, but the architecture
must keep the optimization logic independent from the underlying model
provider.

------------------------------------------------------------------------

# 2. The Problem PromptEasyAI Solves

Many users know what they want from an AI system but do not know how to
express the request effectively.

For example:

### Poor prompt

``` text
make me a resume
```

The request contains an intent, but it lacks useful context:

-   Resume for whom?
-   Which role?
-   Which industry?
-   What experience?
-   What format?
-   What tone?
-   What information should be prioritized?
-   What constraints exist?

A conventional LLM can still produce an answer, but the quality depends
heavily on assumptions.

PromptEasyAI should instead transform the request into something closer
to:

``` text
Create a professional, ATS-friendly resume for a third-year
Computer Science student applying for software engineering
internships. Prioritize programming projects, technical skills,
relevant coursework, internships, and measurable achievements.
Use a concise one-page structure and action-oriented bullet points.
Do not invent experience or qualifications that were not provided.
```

The optimized prompt remains the user's request, but it becomes
substantially more actionable.

------------------------------------------------------------------------

# 3. Core Product Philosophy

PromptEasyAI follows several principles.

## 3.1 Preserve intent

The most important rule is:

> **Improve the prompt without changing what the user actually wants.**

The optimizer must not silently introduce a different objective.

For example:

``` text
User:
"Explain neural networks simply."
```

The system should not transform this into:

``` text
"Write an advanced academic paper about neural network architectures."
```

That would be technically more detailed but semantically wrong.

Instead:

``` text
"Explain neural networks in simple, beginner-friendly language.
Use an intuitive analogy, explain the basic components and how
they work together, and avoid unnecessary mathematical detail."
```

The original intent remains intact.

------------------------------------------------------------------------

## 3.2 Improve clarity, not merely length

A longer prompt is not automatically a better prompt.

PromptEasyAI should optimize for:

-   clarity
-   specificity
-   context
-   constraints
-   output requirements
-   ambiguity reduction
-   consistency
-   actionability

It should **not** simply add unnecessary words.

------------------------------------------------------------------------

## 3.3 Model agnostic

The architecture should allow the underlying model to be replaced.

Conceptually:

``` text
PromptEasyAI Core
       │
       ├── LLM Provider A
       ├── LLM Provider B
       ├── Local Model
       └── Future Provider
```

The optimization pipeline should not be tightly coupled to one provider.

------------------------------------------------------------------------

## 3.4 Deterministic structure where possible

LLMs are useful for understanding and rewriting language, but the
surrounding system should use deterministic logic wherever practical.

For example:

-   schema validation
-   input validation
-   output validation
-   required field checks
-   length constraints
-   error handling
-   configuration
-   provider abstraction

The LLM should not be responsible for everything.

------------------------------------------------------------------------

# 4. V0.1 Product Definition

The initial V0.1 core has one fundamental job:

> **Accept a raw user prompt and return a clearer, more specific,
> validated prompt while preserving the original intent.**

### Input

``` text
A raw string supplied by the user.
```

### Output

Conceptually:

``` text
An optimized prompt.
```

The internal implementation may contain structured intermediate
representations, but the core user-facing contract should remain simple.

------------------------------------------------------------------------

# 5. V0.1 Scope

## In scope

V0.1 should focus on:

1.  Receiving a raw prompt.
2.  Validating that the input is usable.
3.  Understanding the user's apparent intent.
4.  Identifying ambiguity and missing useful context.
5.  Improving the prompt.
6.  Preserving the user's original goal.
7.  Validating the generated result.
8.  Returning the optimized prompt.
9.  Handling failures cleanly.
10. Keeping the implementation provider-independent.

## Explicitly not the priority for V0.1

Do not prematurely build:

-   a full autonomous agent
-   a large multi-model orchestration system
-   a complex user dashboard
-   social features
-   enterprise administration
-   billing infrastructure
-   massive prompt libraries
-   complicated RAG systems
-   unnecessary microservices
-   model training from scratch
-   a custom foundation model

The first objective is to prove that the **prompt optimization core
works reliably**.

------------------------------------------------------------------------

# 6. High-Level Architecture

The target architecture is:

``` text
                         ┌──────────────────────┐
                         │      User Input      │
                         │      Raw Prompt      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Input Validation   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Prompt Analyzer     │
                         │                      │
                         │ - Intent             │
                         │ - Context            │
                         │ - Ambiguity          │
                         │ - Constraints        │
                         │ - Output expectation │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Prompt Optimizer     │
                         │                      │
                         │ Uses LLM abstraction │
                         │ to improve prompt    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Output Validator     │
                         │                      │
                         │ - Valid structure    │
                         │ - Intent preserved   │
                         │ - Non-empty output   │
                         │ - Safe formatting    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Optimized Prompt    │
                         └──────────────────────┘
```

------------------------------------------------------------------------

# 7. Recommended Internal Pipeline

The logical pipeline should be separated into clear stages.

## Stage 1 --- Raw Prompt

Example:

``` text
make python project
```

The system receives the user's original input without changing it.

------------------------------------------------------------------------

## Stage 2 --- Input Validation

Check basic conditions such as:

-   Is the input a string?
-   Is it empty?
-   Is it only whitespace?
-   Is it within the supported input limits?
-   Is the request structurally usable?

Example:

``` text
""
```

should fail cleanly rather than being sent unnecessarily to the LLM.

------------------------------------------------------------------------

## Stage 3 --- Prompt Analysis

The system should identify useful semantic properties of the request.

A conceptual analysis object could contain:

``` text
intent
context
task
target
constraints
desired_output
audience
tone
ambiguities
missing_information
```

Not every prompt will have every field.

The system should avoid inventing information.

For example:

``` text
"Create a Python calculator."
```

does not justify assuming:

``` text
GUI application
Tkinter
desktop
scientific calculator
```

unless those details are provided or clearly required by the task.

------------------------------------------------------------------------

# 8. Intent Preservation

Intent preservation is the central quality requirement.

The optimizer should conceptually compare:

``` text
Original Intent
      ↓
Optimized Prompt
```

and ask:

> Does the optimized prompt still request the same fundamental thing?

A useful conceptual rule is:

``` text
Optimization = Increased clarity + Increased specificity
               - Intent drift
               - Unsupported assumptions
```

The system should prefer a slightly less detailed prompt over a highly
detailed prompt that invents requirements.

------------------------------------------------------------------------

# 9. Handling Missing Information

A major design decision is how PromptEasyAI deals with missing
information.

Not every missing detail requires a user question.

For example:

``` text
"Explain Python."
```

There are many possible interpretations, but the system can reasonably
improve it to:

``` text
"Explain the Python programming language in beginner-friendly
terms. Cover what Python is, its main characteristics, common
use cases, and a few simple examples."
```

However, for a request such as:

``` text
"Write an application for me."
```

the missing context may be too important to safely assume.

The architecture should therefore support a future distinction between:

``` text
Safe to optimize directly
```

and:

``` text
Needs clarification
```

This distinction is important for future versions.

------------------------------------------------------------------------

# 10. Prompt Optimization Strategy

The optimizer should generally improve the following dimensions.

## 10.1 Task clarity

What exactly should the AI do?

``` text
"tell me about databases"
```

could become:

``` text
"Explain what databases are, why they are used, the difference
between relational and non-relational databases, and give simple
examples of common use cases."
```

------------------------------------------------------------------------

## 10.2 Context

Add context only when it exists in the original request or can be safely
inferred.

Do not fabricate user information.

------------------------------------------------------------------------

## 10.3 Constraints

Useful constraints can include:

-   length
-   format
-   audience
-   technical depth
-   tone
-   technologies
-   required sections
-   exclusions

Only introduce constraints when they are supported by the user's intent
or are generic improvements that do not change the task.

------------------------------------------------------------------------

## 10.4 Output format

When the intended output is unclear but a useful format can be safely
specified, make it explicit.

For example:

``` text
"compare python and java"
```

could become:

``` text
"Compare Python and Java in a concise table covering syntax,
performance, memory management, ecosystem, common use cases,
learning curve, and typical application domains. End with a
short summary of when each language is a better choice."
```

------------------------------------------------------------------------

## 10.5 Audience

If the user specifies:

``` text
for beginners
```

that should become an explicit optimization constraint.

If no audience is specified, the system should avoid making an
aggressive assumption.

------------------------------------------------------------------------

# 11. LLM Provider Abstraction

The LLM should be hidden behind a provider abstraction.

Conceptually:

``` python
class LLMProvider:
    def generate(self, prompt: str) -> str:
        ...
```

A concrete provider might implement:

``` python
class GroqProvider(LLMProvider):
    ...
```

Future providers could include:

``` text
OpenAIProvider
AnthropicProvider
GeminiProvider
LocalModelProvider
```

The core optimizer should depend on the abstraction rather than directly
depending on one provider.

------------------------------------------------------------------------

# 12. Configuration

Provider configuration should come from environment/configuration rather
than being hard-coded.

For example:

``` text
LLM_PROVIDER=groq
LLM_MODEL=...
API_KEY=...
```

Secrets must never be committed to Git.

Use:

``` text
.env
```

for local secrets and:

``` text
.env.example
```

for documenting required variables.

------------------------------------------------------------------------

# 13. Structured Data and Validation

The project already uses **Pydantic** as part of its dependency set.

Structured models should be used where they improve reliability.

Conceptually:

``` text
Raw Input
    ↓
Input Model
    ↓
Analyzer
    ↓
Optimization Result
    ↓
Output Model
```

This prevents the project from becoming a collection of unvalidated
dictionaries and loosely structured strings.

------------------------------------------------------------------------

# 14. Current Technology Direction

The current development environment includes:

-   Python
-   Pydantic
-   pytest
-   python-dotenv
-   Groq SDK

The project currently targets:

``` text
Python >= 3.13
```

The exact provider/model implementation may evolve.

The important architectural requirement is that provider-specific code
remains isolated.

------------------------------------------------------------------------

# 15. Testing Strategy

Testing is a first-class requirement.

PromptEasyAI is a language-processing system, so tests should not only
check whether code runs; they should check whether the system behaves
according to the product contract.

## Unit tests

Test:

-   input validation
-   schema validation
-   provider abstraction
-   optimizer logic
-   error handling
-   configuration loading

## Behavioral tests

Examples:

``` text
Input:
"make a resume"

Expected properties:
- remains a resume-generation request
- becomes clearer
- does not invent user experience
- is non-empty
```

Another:

``` text
Input:
"explain recursion to a child"

Expected properties:
- remains about recursion
- preserves child-level audience
- becomes clearer
- does not become an advanced explanation
```

## Regression tests

Every important bug should eventually become a regression test.

------------------------------------------------------------------------

# 16. Quality Criteria for an Optimized Prompt

An optimized prompt should ideally satisfy:

### 1. Intent preservation

The original objective remains unchanged.

### 2. Clarity

The instruction is easier for an AI model to understand.

### 3. Specificity

Relevant details are explicit.

### 4. Actionability

The receiving model can act on it without unnecessary interpretation.

### 5. No fabricated facts

The optimizer must not invent personal facts, qualifications,
requirements, or context.

### 6. Appropriate constraints

Useful output requirements are made explicit when justified.

### 7. Conciseness

Do not add unnecessary verbosity.

### 8. Validity

The returned object/output must satisfy the expected schema.

------------------------------------------------------------------------

# 17. Example End-to-End Flow

## User input

``` text
make me a python project
```

## Analysis

Possible interpretation:

``` text
intent:
  create a Python project

ambiguity:
  project type is unspecified

missing_information:
  domain/use case

safe optimization:
  provide a generic project structure request
```

## Optimized prompt

A possible result:

``` text
Create a Python project with a clean, maintainable project
structure. Include an appropriate directory layout, dependency
management, entry point, configuration handling, README, and
basic tests. Keep the implementation modular and explain the
purpose of each major component. Do not assume a specific
application domain unless one is provided.
```

The exact output does not need to match this wording. The important
requirement is that the **semantic objective is preserved**.

------------------------------------------------------------------------

# 18. What PromptEasyAI Is NOT

PromptEasyAI is not initially:

### A chatbot

It improves instructions; it does not need to answer the underlying task
itself.

### A prompt marketplace

A prompt library can be a future product feature, but it is not the core
engine.

### A model

PromptEasyAI does not need to train its own foundation model.

### A universal AI agent

The initial product does not execute arbitrary tasks on behalf of users.

### A prompt beautifier

Simply making a prompt sound professional is insufficient.

### A text expander

Adding words without adding useful information is not optimization.

------------------------------------------------------------------------

# 19. Long-Term Product Vision

The V0.1 optimizer is the foundation for a much larger system.

The long-term vision is:

> **PromptEasyAI becomes an intelligent layer between humans and AI
> models that understands what the user wants, improves the instruction,
> validates it, and eventually helps users consistently communicate
> their intent to different AI systems.**

Potential future architecture:

``` text
                         ┌────────────────────┐
                         │       User         │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   PromptEasyAI     │
                         │   Intelligence     │
                         └─────────┬──────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
                 ▼                 ▼                 ▼
            Optimization      Validation       Personalization
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ Model Selection /  │
                         │ Provider Layer     │
                         └─────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
           Model A              Model B              Model C
```

------------------------------------------------------------------------

# 20. Future Feature Directions

These are future directions, not requirements for V0.1.

## 20.1 Prompt history

Allow users to see how their prompts evolved.

``` text
Original Prompt
      ↓
Version 1
      ↓
Version 2
      ↓
Final Prompt
```

------------------------------------------------------------------------

## 20.2 Prompt scoring

Provide dimensions such as:

``` text
Clarity:       82/100
Specificity:   76/100
Context:       61/100
Constraints:   70/100
Overall:       78/100
```

The scoring system should eventually be evidence-based rather than
arbitrary.

------------------------------------------------------------------------

## 20.3 Prompt modes

Possible future modes:

``` text
General
Coding
Research
Writing
Business
Education
Data Analysis
Creative
```

The underlying optimization engine should remain shared.

------------------------------------------------------------------------

## 20.4 Model-aware optimization

The long-term system may optimize differently for different models.

For example:

``` text
User intent
    ↓
PromptEasyAI
    ↓
Target model
    ↓
Model-specific optimization
```

But this must remain separate from the initial model-agnostic core.

------------------------------------------------------------------------

## 20.5 Personalization

Future versions could learn how a user prefers prompts to be structured.

For example:

``` text
User preference:
- concise instructions
- technical detail
- Markdown output
```

Personalization must never override the user's current request.

------------------------------------------------------------------------

## 20.6 Prompt feedback loop

Eventually:

``` text
User Prompt
     ↓
Optimization
     ↓
AI Output
     ↓
User Feedback
     ↓
Prompt Improvement
```

This could allow PromptEasyAI to learn which types of prompt
transformations produce better downstream results.

------------------------------------------------------------------------

# 21. Future ML Research Direction

PromptEasyAI may eventually move beyond pure LLM-based rewriting.

A future research pipeline could investigate:

``` text
Raw Prompt
    ↓
Feature Extraction
    ↓
Prompt Quality Representation
    ↓
Optimization Model
    ↓
Candidate Prompts
    ↓
Evaluation
    ↓
Best Prompt
```

Potential research areas include:

-   prompt quality classification
-   semantic similarity
-   intent preservation scoring
-   ambiguity detection
-   prompt difficulty estimation
-   prompt ranking
-   preference learning
-   reinforcement learning from feedback
-   embedding-based semantic comparison
-   model-specific prompt evaluation

However:

> **Do not introduce custom ML training into V0.1 merely because the
> project is called AI/ML.**

The first goal is to establish a reliable product and evaluation
framework.

------------------------------------------------------------------------

# 22. Repository Philosophy

The repository should remain understandable to a developer who has never
seen the project before.

Prefer:

``` text
small modules
clear names
explicit interfaces
type hints
tests
documentation
```

Avoid:

``` text
giant files
hidden global state
hard-coded API keys
provider-specific logic everywhere
unnecessary abstractions
premature microservices
```

------------------------------------------------------------------------

# 23. Suggested Repository Structure

The exact structure can evolve, but the architectural separation should
resemble:

``` text
PromptEasyAI/
│
├── src/
│   └── prompteasy/
│       ├── __init__.py
│       │
│       ├── core/
│       │   ├── analyzer.py
│       │   ├── optimizer.py
│       │   ├── validator.py
│       │   └── pipeline.py
│       │
│       ├── models/
│       │   ├── prompt.py
│       │   └── result.py
│       │
│       ├── providers/
│       │   ├── base.py
│       │   └── groq.py
│       │
│       ├── config/
│       │   └── settings.py
│       │
│       └── utils/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── behavioral/
│
├── docs/
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── ProjectDetails.md
```

This is a target architectural direction, not a command to create every
directory immediately.

------------------------------------------------------------------------

# 24. Development Phases

## Phase 0 --- Concept

Define:

-   problem
-   product goal
-   core principles
-   scope

Status:

``` text
Completed
```

------------------------------------------------------------------------

## Phase 1 --- Core Architecture

Establish:

``` text
raw prompt
    ↓
processing
    ↓
optimized prompt
```

Focus:

-   clean interfaces
-   provider abstraction
-   validation
-   testing
-   minimal viable pipeline

Important principle:

> Keep the engine minimal and model-agnostic.

Status:

``` text
Architectural principles established
```

------------------------------------------------------------------------

## Phase 1.5 --- Current Active Build

Phase 1.5 is the current development phase.

The project was restarted from a clean, explicitly tracked baseline on:

``` text
2026-08-15
```

The purpose of Phase 1.5 is to turn the architectural principles into a
working, testable V0.1 implementation without prematurely expanding the
scope.

Priorities:

1.  Establish the actual package structure.
2.  Implement the core prompt pipeline.
3.  Implement structured models.
4.  Implement provider abstraction.
5.  Connect the initial LLM provider.
6.  Implement validation.
7.  Add unit tests.
8.  Add behavioral/regression tests.
9.  Keep the implementation small and understandable.
10. Document decisions as the system evolves.

------------------------------------------------------------------------

# 25. Current Dependency Direction

The current project configuration includes dependencies in the following
direction:

``` text
groq
pydantic
pytest
python-dotenv
```

Python requirement:

``` text
>= 3.13
```

These dependencies support:

-   LLM communication
-   structured validation
-   automated testing
-   environment configuration

Do not add dependencies without a clear reason.

------------------------------------------------------------------------

# 26. GitHub Copilot Instructions

GitHub Copilot should treat this document as the high-level product and
architecture context for PromptEasyAI.

When generating code, Copilot should follow these rules.

## Rule 1 --- Protect the core goal

Always remember:

``` text
PromptEasyAI = prompt optimization engine
```

not:

``` text
PromptEasyAI = chatbot
```

------------------------------------------------------------------------

## Rule 2 --- Preserve intent

Any optimization logic must prioritize semantic intent preservation.

Never introduce arbitrary assumptions simply to make the prompt longer.

------------------------------------------------------------------------

## Rule 3 --- Keep providers abstract

Core code should not directly depend on Groq-specific APIs unless the
code belongs to the provider implementation layer.

Prefer:

``` text
core → LLMProvider interface → GroqProvider
```

rather than:

``` text
core → Groq SDK directly
```

------------------------------------------------------------------------

## Rule 4 --- Validate structured data

Use Pydantic models for structured application data where appropriate.

Do not rely on undocumented dictionary shapes.

------------------------------------------------------------------------

## Rule 5 --- Test before expanding

When implementing a new behavior:

1.  Define the expected behavior.
2.  Write or update tests.
3.  Implement the behavior.
4.  Run the tests.
5.  Fix regressions.

------------------------------------------------------------------------

## Rule 6 --- Do not over-engineer

If a feature can be implemented cleanly with a small module, do not
introduce:

-   unnecessary frameworks
-   complex design patterns
-   microservices
-   excessive abstraction layers

------------------------------------------------------------------------

## Rule 7 --- Do not invent user information

The optimizer must never fabricate:

-   names
-   experience
-   qualifications
-   organizations
-   project requirements
-   personal preferences
-   facts

unless the user explicitly supplied them.

------------------------------------------------------------------------

## Rule 8 --- Keep original input available

The system should retain the original prompt throughout the pipeline so
that:

``` text
original prompt
```

can be compared against:

``` text
optimized prompt
```

This is important for future intent-preservation evaluation.

------------------------------------------------------------------------

## Rule 9 --- Fail clearly

Failures should be explicit and actionable.

Examples:

``` text
Invalid input
Provider unavailable
Provider configuration missing
Invalid LLM response
Output validation failed
```

Avoid silent failures.

------------------------------------------------------------------------

## Rule 10 --- Documentation is part of the implementation

When an architectural decision changes, update the relevant
documentation.

------------------------------------------------------------------------

# 27. Copilot Mental Model

Before changing code, Copilot should mentally model the project as:

``` text
USER
 │
 │ raw prompt
 ▼
INPUT VALIDATOR
 │
 ▼
PROMPT ANALYZER
 │
 │ semantic understanding
 ▼
PROMPT OPTIMIZER
 │
 │ LLM-assisted transformation
 ▼
OUTPUT VALIDATOR
 │
 ▼
OPTIMIZED PROMPT
```

And separately:

``` text
PROMPT OPTIMIZER
       │
       ▼
  LLM PROVIDER
       │
       ├── Groq
       ├── Future provider
       └── Future local model
```

The provider layer is an implementation detail of the optimization
system, not the identity of the product.

------------------------------------------------------------------------

# 28. Definition of Done for V0.1

V0.1 should not be considered complete merely because an LLM returns
text.

A reasonable V0.1 completion criterion is:

``` text
Given a valid raw user prompt,
PromptEasyAI can reliably produce
a clearer and more specific prompt,
while preserving the user's intent,
without fabricating unsupported information,
and the result passes structural validation
and automated tests.
```

The system should also have:

-   clean package structure
-   provider abstraction
-   configuration handling
-   error handling
-   unit tests
-   behavioral tests
-   documentation
-   reproducible local setup

------------------------------------------------------------------------

# 29. Example Acceptance Tests

## Test A --- Simple request

Input:

``` text
make a website
```

Expected:

-   remains a website-generation request
-   becomes more actionable
-   does not assume an unrelated business
-   does not invent branding

------------------------------------------------------------------------

## Test B --- Explicit audience

Input:

``` text
explain machine learning to a beginner
```

Expected:

-   remains an ML explanation
-   preserves beginner audience
-   uses appropriate technical depth
-   becomes clearer

------------------------------------------------------------------------

## Test C --- Coding request

Input:

``` text
fix my python code
```

Expected:

-   remains a debugging request
-   does not fabricate the missing code
-   may explicitly ask for the code if necessary
-   does not claim that a fix was already performed

------------------------------------------------------------------------

## Test D --- Personal information protection

Input:

``` text
write a resume for me
```

Expected:

-   does not invent education, experience, skills, or achievements
-   may request missing information or create a structured prompt that
    clearly indicates what information is required

------------------------------------------------------------------------

## Test E --- Intent preservation

Input:

``` text
compare React and Angular
```

Expected:

-   remains a comparison
-   does not turn into a tutorial
-   does not select a winner without justification
-   may specify useful comparison dimensions

------------------------------------------------------------------------

# 30. Important Engineering Tradeoff

There is an inherent tension between:

``` text
specificity
```

and:

``` text
intent preservation
```

More details can make a prompt better, but unsupported details can
change the task.

Therefore PromptEasyAI should optimize according to:

``` text
Useful specificity > maximum specificity
```

and:

``` text
Intent preservation > stylistic improvement
```

This principle should guide both prompts sent to the LLM and
deterministic validation logic.

------------------------------------------------------------------------

# 31. Long-Term End Goal

The ultimate goal is not simply to create a tool that rewrites prompts.

The larger goal is to build a **reliable AI communication layer**.

Humans express goals in natural language.

AI models require precise instructions.

PromptEasyAI should increasingly bridge that gap:

``` text
Human Intent
     ↓
Natural Language
     ↓
PromptEasyAI
     ↓
Structured / Optimized Instruction
     ↓
AI Model
     ↓
Better Output
```

Over time, PromptEasyAI could become an intelligence layer that:

-   understands intent
-   detects ambiguity
-   improves instructions
-   preserves user constraints
-   validates prompt quality
-   adapts prompts to different models
-   learns from feedback
-   helps users build better prompting habits

But the foundation must remain the same:

> **Understand what the user means, improve how it is communicated to an
> AI, and do not change what the user actually asked for.**

------------------------------------------------------------------------

# 32. Final Project Definition

### One-sentence definition

**PromptEasyAI is a model-agnostic AI prompt optimization engine that
transforms raw user instructions into clearer, more specific, validated
prompts while preserving the user's original intent.**

### V0.1 definition

``` text
Input:
    Raw user prompt

Process:
    Validate
    → Analyze
    → Optimize
    → Validate

Output:
    Optimized prompt
```

### Long-term definition

``` text
PromptEasyAI
    =
AI communication intelligence layer
between human intent and AI execution.
```

------------------------------------------------------------------------

# 33. Instructions for Future Development Sessions

When continuing PromptEasyAI development:

1.  Read `ProjectDetails.md` first.
2.  Treat Phase 1.5 as the current active phase unless explicitly
    changed.
3.  Preserve the model-agnostic architecture.
4.  Preserve intent above all other optimization goals.
5.  Keep V0.1 minimal.
6.  Prefer small, testable modules.
7.  Do not introduce unnecessary dependencies.
8.  Do not invent requirements that the user did not specify.
9.  Update tests whenever behavior changes.
10. Update documentation when architectural decisions change.
11. Do not jump to future features before the V0.1 core is stable.
12. When uncertain, choose the simplest implementation that satisfies
    the current project contract.

------------------------------------------------------------------------

# 34. Current Priority

The immediate priority is:

``` text
Build a reliable V0.1 prompt optimization core.
```

Not:

``` text
Build the entire future PromptEasyAI platform.
```

The project should progress incrementally:

``` text
Stable Core
    ↓
Reliable Evaluation
    ↓
Better Optimization
    ↓
Useful Product Interface
    ↓
Advanced Intelligence
```

The quality of the foundation determines the quality of everything built
on top of it.
