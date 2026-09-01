# PromptEasyAI

PromptEasyAI is intended to be an AI prompt enhancer, not just a prompt analyzer.

The current project already includes the core architecture for analysis, validation, provider abstraction, CLI usage, and a FastAPI service. That foundation is useful. However, the current optimizer is still too weak to be considered a robust prompt enhancer.

## What the project does well

The repository already supports:

- structured prompt analysis
- output validation through Pydantic
- provider abstraction for Groq and offline use
- CLI and web-flow entry points
- deterministic local testing without network access

This gives the project a strong base for the next phase.

## The actual problem

The existing optimized output is not truly a ready-to-send prompt for another LLM.

I verified this directly by running the current code with a realistic prompt:

```powershell
.\.venv\Scripts\python -c "from prompteasy import PromptAnalyzer; from prompteasy.llm import OfflineProvider; a = PromptAnalyzer(provider=OfflineProvider()).analyze('Build a login page for a SaaS product'); print(a.optimized_prompt)"
```

Observed output:

```text
Build a login page for a SaaS product. Be accurate. Ask for missing details. State assumptions. Follow user constraints and format.
```

This is not a proper optimized prompt. It is a generic sentence. It does not define:

- objective and success criteria
- target audience
- user flow
- required screens and states
- accessibility expectations
- output structure
- acceptance criteria
- assumptions and missing information

A real prompt enhancer must create a prompt that another LLM can act on immediately without needing extra explanation.

## Product goal

PromptEasyAI should help a user turn a weak or vague prompt into a complete, implementation-ready instruction for any downstream LLM.

The final system should behave like this:

```text
Weak prompt
  |
  v
Task extraction
  |
  v
Missing-info detection
  |
  v
Requirements and constraints collection
  |
  v
Structured prompt assembly
  |
  v
Ready-to-send prompt for downstream AI
```

## What a strong optimized prompt looks like

Instead of a generic sentence, the system should generate a prompt similar to this:

```text
You are helping create a modern login page for a SaaS product.

Objective:
Create a secure, polished login experience for a web application.

Context:
- Product type: SaaS app
- Target users: returning users signing in
- Platform: web application
- Design style: modern, clean, trustworthy

Requirements:
- Support email and password sign-in
- Validate empty and invalid input
- Show clear error states and success feedback
- Keep the experience responsive on mobile and desktop
- Follow accessibility best practices

Deliverables:
- UI structure
- interaction behavior
- validation logic
- edge case handling

Acceptance criteria:
- Clear login flow
- Fast and understandable experience
- Accessible labels and focus states
- Professional and conversion-friendly design

Assumptions:
- If technology or branding details are missing, use a standard modern web stack and neutral SaaS design.

Output format:
Provide a concise, implementation-ready specification with sections for layout, behavior, validation, and edge cases.
```

This is the correct benchmark for the project: a prompt that is functional, structured, and ready to send.

## Corrected system architecture

### 1. Input normalizer
- validate the raw prompt
- detect empty or malformed input
- preserve the original user intent

### 2. Task understanding layer
- classify the goal
- identify domain, deliverables, and target user
- extract platform, audience, and constraints

### 3. Missing information engine
- detect missing facts that materially affect delivery
- rank clarifying questions by impact
- ask only the most important questions when needed

### 4. Constraint collector
- gather functional, technical, UX, and security constraints
- avoid inventing unsupported details

### 5. Prompt assembler
- produce a final structured prompt with:
  - objective
  - context
  - assumptions
  - requirements
  - deliverables
  - acceptance criteria
  - output format

### 6. Quality validation layer
- verify the final prompt is action-oriented and specific
- reject vague or fabricated rewrites
- confirm intent remains preserved

### 7. Provider-agnostic output pipeline
- same enhancement engine can work across Groq, OpenAI, Anthropic, or local models
- output format is consistent regardless of provider

## New roadmap for the real product

### Phase 1: Prompt-spec foundation
- define a canonical prompt-spec schema
- convert raw text into structured objective/context/constraint records
- add validation for required fields

### Phase 2: Clarification engine
- score missing facts by impact
- ask only the key questions before final assembly
- merge user answers without mutating intent

### Phase 3: Prompt assembly
- build section-based templates for coding, UX, research, analysis, and general tasks
- assemble a final prompt that is ready to send to another LLM

### Phase 4: Quality and anti-hallucination checks
- reject unsupported assumptions
- detect under-specified prompts
- enforce intent preservation and output-contract clarity

### Phase 5: Provider abstraction and benchmarking
- test the same enhancer across providers
- benchmark prompt readiness and actionability
- create release gates for prompt quality

### Phase 6: API, CLI, and UI upgrade
- expose the final enhanced prompt cleanly
- allow preview, editing, and export
- align the web interface around real prompt enhancement

## Expected outcome

The system should no longer produce a generic sentence. It should produce a usable, structured, high-quality prompt that a downstream model can act on immediately without needing the user to explain the task again.

This is the direction the project should move toward.

## Project status

The repository has strong foundational work, but the current optimizer must be upgraded to a true prompt-enhancement engine. The next milestone is a structured prompt compiler that turns a basic idea into a complete prompt package ready for any LLM.

See [ProjectDetails.md](ProjectDetails.md) for the original product intent and [plan.md](plan.md) for the corrected implementation roadmap.
