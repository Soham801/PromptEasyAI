# PromptEasyAI Implementation Blueprint

## 1. Objective

Build PromptEasyAI as a model-agnostic AI prompt enhancement engine that converts a vague or partial user request into a complete, ready-to-send prompt for another LLM.

The system must not simply rephrase text. It must:

- understand the user’s true intent,
- identify missing facts and risk,
- classify the task family,
- gather constraints, audience, format, and success criteria,
- assemble a structured final prompt,
- validate that the result is faithful, specific, and usable,
- remain provider-agnostic and offline-testable.

## 2. Product definition

### Primary user value

A user enters a rough idea such as:

```text
Build a login page for a SaaS product
```

The system returns a prompt like:

```text
You are helping build a modern SaaS login experience.

Objective:
Create a secure, polished login page for a web application.

Context:
- Product type: SaaS product
- Users: end users signing in
- Platform: web app
- Tone: modern, trustworthy, conversion-friendly

Requirements:
- Support email/password sign-in
- Validate empty and malformed input
- Provide accessible error feedback
- Ensure mobile and desktop responsiveness

Deliverables:
- UI structure
- interaction flow
- validation states
- edge-case handling

Acceptance criteria:
- Clear and intuitive UX
- Accessible form controls
- Good visual hierarchy and conversion-focused layout

Output format:
Provide an implementation-ready specification with layout, behavior, validation, and edge cases.
```

This is the target product behavior.

## 3. Architecture overview

### Core layers

1. Input layer
   - raw prompt ingestion
   - validation and normalization
   - user/session context

2. Prompt understanding layer
   - intent extraction
   - task-family classification
   - missing-info detection
   - risk scoring

3. Prompt specification layer
   - structured PromptSpec object
   - explicit fields for objective, constraints, audience, etc.
   - traceability to original requirements

4. Enhancement layer
   - template routing
   - clarification-first logic
   - prompt assembly

5. Validation layer
   - intent-preservation checks
   - unsupported-claim detection
   - requirement recall checks
   - specificity and boilerplate scoring

6. Provider layer
   - offline deterministic provider
   - Groq provider
   - future providers

7. Application layer
   - CLI
   - FastAPI API
   - web UI
   - persistence and history

## 4. System design

### 4.1 Data model: PromptSpec

Add a core internal model with versioning.

```python
class PromptSpec(BaseModel):
    schema_version: str
    original_prompt: str
    objective: str
    task_family: str
    context: list[str]
    audience: str | None
    platform: str | None
    constraints: list[str]
    deliverables: list[str]
    success_criteria: list[str]
    assumptions: list[str]
    unresolved_questions: list[str]
    output_format: str | None
    risk_level: str
    confidence: float
    evidence_links: list[str]
```

This model must be the canonical internal representation for optimization.

### 4.2 Task families

Supported task families:

- build_implement
- analyze_evaluate
- write_create
- summarize_distill
- compare_choose
- plan_design
- debug_fix
- research_synthesize

Each family routes to a prompt template.

### 4.3 Missing-information scoring

A service should evaluate each prompt for missing critical details:

- target audience
- platform
- output format
- domain context
- performance or quality constraints
- validation and acceptance criteria
- data source or reference material

The scoring model should output:

- missing fact list
- severity score
- clarification priority
- assumption placeholders

### 4.4 Output modes

The optimizer should select one of these modes:

- direct
- clarification_first
- template_assisted
- synthesis_with_constraints

Selection should depend on:

- task complexity,
- missing fact severity,
- risk level,
- whether the user explicitly requests output structure.

## 5. Core service architecture

### 5.1 Module layout

```text
src/prompteasy/
  __init__.py
  analyzer.py
  models.py
  optimizer.py
  prompt_spec.py
  task_classifier.py
  clarification_engine.py
  template_catalog.py
  prompt_assembler.py
  validator.py
  llm.py
  config.py
  api.py
  service.py
  storage.py
  benchmark.py
  evaluator.py
  cli.py
```

### 5.2 Responsibilities

#### analyzer.py
Responsible for raw prompt analysis and formatting into a structured intermediate result.

#### prompt_spec.py
Defines PromptSpec and related validation.

#### task_classifier.py
Classifies the task family and selects the prompt strategy.

#### clarification_engine.py
Determines what information is missing and if clarification is required.

#### template_catalog.py
Stores prompt templates per task family.

#### prompt_assembler.py
Builds the final prompt from PromptSpec + template.

#### validator.py
Checks faithfulness, completeness, unsupported assumptions, and risk.

#### optimizer.py
Coordinates the full enhancement pipeline.

#### llm.py
Abstraction for offline, Groq, and future providers.

## 6. Enhancement pipeline

### Stage 1: Normalize input

Responsibilities:

- trim and validate string input,
- reject blanks and malformed values,
- preserve the original prompt exactly in storage,
- record raw input for traceability.

### Stage 2: Extract intent and context

Responsibilities:

- identify user objective,
- determine task family,
- gather audience, platform, domain, tone, and constraints,
- capture explicit requirements from source text.

### Stage 3: Score missing information

Responsibilities:

- detect absent facts that materially affect output,
- rank by impact,
- decide whether to ask a clarifying question or use a placeholder.

### Stage 4: Select template

Responsibilities:

- match task family to a template,
- bind task-specific slots,
- preserve evidence-backed user requirements,
- avoid injecting unknown information.

### Stage 5: Assemble prompt

Responsibilities:

- build final prompt sections,
- include objective, constraints, deliverables, and acceptance criteria,
- clearly label assumptions and unresolved questions,
- keep final prompt specific and concise.

### Stage 6: Validate final prompt

Responsibilities:

- verify no unsupported facts are introduced,
- verify no user requirement is dropped,
- verify the final prompt is materially better than the original,
- reject or flag low-confidence results.

### Stage 7: Return structured response

Return:

```json
{
  "original_prompt": "...",
  "prompt_spec": {...},
  "optimized_prompt": "...",
  "missing_information": [...],
  "unresolved_questions": [...],
  "assumptions": [...],
  "quality_signals": {...},
  "validation": {
    "valid": true,
    "warnings": []
  }
}
```

## 7. Prompt template model

A template should contain structured slots and metadata.

```python
class PromptTemplate(BaseModel):
    name: str
    task_family: str
    description: str
    required_sections: list[str]
    optional_sections: list[str]
    constraints: list[str]
    style_instructions: list[str]
```

Example template families:

- coding_task
- planning_task
- analysis_task
- comparison_task
- writing_task
- research_task
- ux_design_task

Each template must be deterministic and evidence-driven.

## 8. Clarification strategy

The system should never guess important missing facts silently.

### Clarification rules

- Ask only for high-impact missing information.
- Prefer one or two critical questions over long blocking forms.
- Use placeholders when a fact is missing but defaulting would be safe and clearly labeled.
- Mark any assumption as an assumption, never as fact.

### Example

If the prompt is:

```text
Create a dashboard
```

The system may ask:

- What type of dashboard is needed?
- Who is the audience?
- What metrics or KPIs matter?
- What output format is expected?

Only if there is enough context may it proceed with a placeholder version.

## 9. Validation framework

### 9.1 Requirements coverage

Ensure every explicit requirement from the original prompt is represented in the final prompt.

### 9.2 Unsupported detail rejection

Reject prompt rewrites that add:

- invented product details,
- fake metrics,
- names, numbers, or tools not present in the source,
- unsupported constraints,
- fabricated assumptions disguised as facts.

### 9.3 Intent drift detection

Check whether the enhanced prompt changes the original goal meaningfully.

### 9.4 Specificity scoring

Measure whether the final prompt is materially more actionable than original input.

### 9.5 Boilerplate penalty

Penalize generic filler that adds little value.

### 9.6 Final gate

The final prompt is accepted only if all required checks pass:

- intent preserved,
- requirement coverage high,
- unsupported facts absent,
- output format clear,
- missing information surfaced.

## 10. Offline testing strategy

The project must remain deterministic and offline-safe.

### Test categories

1. Unit tests
   - PromptSpec validation
   - task classification
   - missing-info scoring
   - template selection
   - prompt assembly
   - validation rules

2. Integration tests
   - full pipeline from raw prompt to final prompt
   - offline provider flow
   - API endpoint flow
   - CLI flow

3. Benchmark tests
   - weak prompt -> strong prompt transformation
   - ambiguous prompt handling
   - conflict detection
   - requirement retention
   - hallucination-risk detection

### Required benchmark sets

- vague prompts
- technical prompts
- role-based prompts
- format-critical prompts
- adversarial prompts
- coding prompts
- planning prompts
- comparison prompts
- domain-heavy prompts
- underspecified prompts

## 11. API design

### Endpoints

#### POST /api/analyze
Request:

```json
{
  "prompt": "Build a login page for a SaaS product"
}
```

Response:

```json
{
  "original_prompt": "Build a login page for a SaaS product",
  "prompt_spec": {...},
  "optimized_prompt": "...",
  "missing_information": [],
  "unresolved_questions": ["Who is the target user?"],
  "assumptions": ["Defaulting to a standard SaaS web flow."],
  "quality_signals": {
    "specificity_delta": 0.82,
    "intent_preservation": 1.0,
    "hallucination_risk": 0.0
  }
}
```

#### POST /api/clarify
Provides missing information prompts and question handling.

#### POST /api/benchmark
Runs benchmark comparison and returns JSON metrics.

#### GET /health
Service health and environment status.

## 12. CLI design

### Commands

```bash
python -m prompteasy.cli analyze --text "Build a login page for a SaaS product"
python -m prompteasy.cli benchmark
python -m prompteasy.cli compare --baseline offline --candidate offline
python -m prompteasy.cli demo --text "..."
```

CLI output should include:

- original prompt,
- task family,
- extracted context,
- missing information,
- final optimized prompt,
- validation result,
- quality score.

## 13. Web UI design

### Core screen states

- empty state
- input editor state
- analysis state
- validation state
- final prompt review state
- clarify-needed state

### UX workflow

1. User enters raw prompt
2. System analyzes and classifies task
3. System shows missing information and assumptions
4. System presents enhanced prompt preview
5. User can review/edit/send/export

### UI contract

- raw prompt displayed separately from enhanced prompt
- missing facts visible and actionable
- assumptions labeled clearly
- final prompt editable
- copy/export supported

## 14. Persistence and storage

### Data stores

- SQLite for local prompt history
- optional per-user metadata
- session-scoped prompt history
- saved prompt templates and user preferences

### Store schema

- prompt_history
- prompt_versions
- user_preferences
- template_catalog
- benchmark_runs

## 15. Security and compliance

### Must-haves

- no secrets in source control
- environment-variable-based config
- per-user isolation for stored records
- optional authentication for persistence endpoints
- no training on user prompt data without explicit opt-in
- clear deletion and export support

## 16. Benchmark design

### Benchmark categories

- weak prompt to strong prompt conversion
- task family classification accuracy
- requirement preservation
- output format preservation
- missing-info handling
- ambiguous prompt behavior
- conflict detection
- prompt injection resistance
- low-quality generic rewrite detection

### Scorecard

Each benchmark case should score:

- requirement_coverage
- intent_preservation
- hallucination_risk
- specificity_delta
- boilerplate_penalty
- clarification_value
- final_prompt_readiness

### Release gate

A release should fail if:

- requirement coverage is too low,
- hallucination risk is non-zero,
- intent drift is detected,
- generic boilerplate dominates the final output,
- benchmark quality regresses below the accepted threshold.

## 17. Development phases

### Phase A: Foundation and contracts

- PromptSpec model
- validation logic
- task family enums
- offline deterministic provider
- benchmarking skeleton

### Phase B: Enhancement engine

- missing-info scoring
- clarification engine
- template catalog
- prompt assembler
- validation layer

### Phase C: API and CLI

- /api/analyze
- benchmark endpoint
- CLI commands
- production-ready error handling

### Phase D: UI and persistence

- prompt review/edit screen
- saved history
- configuration persistence
- user preferences

### Phase E: Release hardening

- benchmark gates
- security review
- production config validation
- deployment readiness

## 18. Delivery checklist

### Engineering checklist

- [ ] PromptSpec schema defined
- [ ] Task classifier implemented
- [ ] Missing info engine implemented
- [ ] Template catalog created
- [ ] Prompt assembler built
- [ ] Validator completed
- [ ] Offline provider deterministic
- [ ] CLI updated
- [ ] API updated
- [ ] UI updated
- [ ] Database schema implemented
- [ ] Benchmarks in place
- [ ] Release gate active

### Product checklist

- [ ] Weak prompt becomes strong prompt
- [ ] User intent preserved
- [ ] Missing facts surfaced
- [ ] Output is ready to send to another LLM
- [ ] Quality metrics measurable
- [ ] Product works without network access in test mode

## 19. Success definition

The project is successful when a raw prompt is transformed into an actionable, structured, send-ready instruction that is materially better than the source and requires little to no follow-up clarification.

That is the true definition of a prompt enhancer.

## 20. Final recommendation

The next implementation priority is to replace the current generic rewrite flow with a structured PromptSpec-driven compiler pipeline. That is the most important technical step toward building a genuinely useful AI prompt enhancement product.
