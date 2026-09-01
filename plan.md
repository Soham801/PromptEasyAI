# PromptEasyAI Delivery Plan

## 1. Executive summary

PromptEasyAI has now moved from a generic prompt rewriter to a structured prompt compiler. The key root cause was identified and corrected: the optimizer was producing boilerplate text instead of a specification-rich prompt. The architecture is sound, and the project now has a concrete internal contract for quality.

The current verified result is not a vague sentence anymore. The system now produces structured output with explicit sections for Objective, Requirements, and Acceptance criteria, which is the minimum bar for a downstream-ready prompt.

Verified evidence:

```powershell
.\.venv\Scripts\python -m pytest -q tests/test_optimizer.py
```

Result:

```text
10 passed in 0.40s
```

This confirms the optimization path is now producing a materially improved prompt and that the regression contract is stable.

## 2. Product definition

### 2.1 Product mission

PromptEasyAI is a model-agnostic AI prompt enhancement engine that turns weak or partial user input into a clear, structured, implementation-ready prompt for another LLM.

The system must:

- preserve the original user intent,
- identify missing facts and high-impact ambiguity,
- ask clarification questions only when necessary,
- compile a task-ready prompt with context, constraints, deliverables, and acceptance criteria,
- remain deterministic and offline-testable,
- avoid unsupported assumptions.

### 2.2 Correct output standard

The output should be a prompt compiler result, not a paraphrase. A strong final prompt should contain:

- Objective
- Context
- Requirements
- Deliverables
- Acceptance criteria
- Assumptions / unresolved questions
- Output format

This is the difference between a generic rewrite and a usable instruction.

## 3. Current status: what is already complete

### 3.1 Completed items

- Root cause analysis completed and validated.
- Weak generic optimizer output was identified and fixed.
- PromptSpec scaffolding was introduced in [src/prompteasy/prompt_spec.py](src/prompteasy/prompt_spec.py).
- Offline optimization path was updated in [src/prompteasy/llm.py](src/prompteasy/llm.py).
- Question-first mode now explicitly asks for missing details instead of guessing.
- Offline, deterministic prompt assembly is now in place for common task families such as login and dashboard flows.
- Regression tests were added and validated for the structured prompt requirement.

### 3.2 Verified behavioral contract

The current system now satisfies this contract:

- output starts with the original user prompt when in question-first mode,
- output includes the missing-details instruction,
- output includes Objective, Requirements, and Acceptance criteria for structured tasks,
- output remains offline-safe and deterministic.

## 4. Root cause and fix summary

### 4.1 Root cause

The previous optimizer behavior was a shallow rewrite. It appended generic sentences like:

```text
Be accurate. Ask for missing details. State assumptions. Follow user constraints and format.
```

This did not create a usable instruction for a downstream model. It lacked a structured specification and therefore failed the core product promise.

### 4.2 Fix

The project is now using a task-aware compiler model that converts the request into a structured PromptSpec and then renders a final prompt with explicit sections. This makes the pipeline closer to a prompt assembly system than a rephrase engine.

## 5. Correct architecture target

### 5.1 Core components

1. Input normalization
   - preserve raw prompt
   - validate empty or malformed input
   - keep original intent intact

2. Task understanding
   - detect task family
   - identify audience, platform, domain, tone, and constraints
   - surface missing-info severity

3. PromptSpec compiler
   - objective
   - context
   - requirements
   - deliverables
   - acceptance criteria
   - assumptions
   - unresolved questions
   - output format

4. Clarification engine
   - ask only for high-impact missing details
   - avoid nuisance questions for low-impact gaps

5. Validation layer
   - check requirement coverage
   - reject unsupported claims or made-up details
   - confirm final output is actionable and faithful

6. Provider abstraction
   - offline provider
   - Groq provider
   - future providers without changing core logic

## 6. Updated roadmap

### Phase 0: Product reset and quality baseline
Status: complete

Achievements:
- product direction clarified
- weak optimizer issue diagnosed
- quality bar explicitly defined
- regression test locked in

### Phase 1: Production-quality PromptSpec compiler
Priority: current

Goal:
Turn the prototype compiler into the core engine of PromptEasyAI.

Tasks:
- formalize the PromptSpec schema and validation rules,
- expand task families beyond login/dashboard,
- create reusable templates for build, analyze, compare, plan, and write tasks,
- add missing-information scoring and clarification prioritization,
- ensure all generated prompts have objective, constraints, deliverables, and acceptance criteria,
- run deterministic offline benchmarks across representative prompt types.

Acceptance criteria:
- every major task family produces a structured prompt,
- missing fact handling is explicit and non-random,
- final prompts are ready to send to another LLM without extra explanation.

### Phase 2: Validation and benchmark maturity
Goal:
Move beyond anecdotal quality and into measured quality.

Tasks:
- create benchmark prompts for weak vs strong output,
- add automated checks for requirement retention and unsupported assumptions,
- score final output clarity, completeness, and actionability,
- compare offline and provider-backed outputs for parity.

Acceptance criteria:
- quality scores are reproducible,
- benchmark regressions are caught before release,
- prompt generation remains faithful to user intent.

### Phase 3: Product integration
Goal:
Expose the compiler through the app’s real interfaces.

Tasks:
- integrate the structured compiler into CLI and API flows,
- expose result metadata like task family, missing facts, and confidence,
- preserve prompt history for comparison and iteration,
- surface clearer provider and validation feedback.

Acceptance criteria:
- users can generate enhanced prompts through CLI/API without custom scripting,
- the system communicates its assumptions and missing data clearly.

### Phase 4: Research and scale-up
Goal:
Make the product extensible and ready for broader prompt families.

Tasks:
- add domain-specific templates for product, coding, research, and content work,
- support richer clarification flows,
- tune quality against user benchmark data,
- evaluate whether a stronger runtime or external provider tier is needed.

Acceptance criteria:
- task-family coverage expands without losing determinism,
- result quality remains stable across broader domains.

## 7. Definition of done

PromptEasyAI is ready for the next serious product milestone when all of the following are true:

- the core prompt compiler produces a structured prompt for the majority of common tasks,
- missing facts are surfaced explicitly and not invented,
- the prompt includes objective, requirements, deliverables, and acceptance criteria,
- validation catches unsupported details and quality drift,
- CLI/API flows use the same compiler as the offline engine,
- benchmark regression tests remain green.

## 8. Risk management

### Key risk: generic output drift
Mitigation: enforce a prompt contract that requires structured sections in every optimized prompt.

### Key risk: unsupported assumptions
Mitigation: separate explicit facts from missing facts; do not guess when confidence is low.

### Key risk: poor question-first behavior
Mitigation: rank clarification requests by impact and only ask high-value questions.

### Key risk: quality becoming provider-dependent
Mitigation: keep validation and prompt assembly independent from any one model provider.

## 9. Immediate next action

The next phase must focus on productionizing the compiler itself:

1. finalize structured PromptSpec validation,
2. expand templates and task-family coverage,
3. wire missing-information scoring into the optimizer,
4. add benchmark-level quality testing,
5. integrate the same compiler into the public CLI/API path.

This is the correct next step because it converts the proven prototype into a product-grade prompt enhancement engine without drifting away from the core mission.
- all product docs and planning materials state the same goal
- prompt quality is defined by actionability and readiness, not just wording improvement

### Phase 1: PromptSpec model

Goal:
Turn raw prompt text into a structured, validated specification.

Deliverables:
- versioned PromptSpec schema
- deterministic validation
- extraction of objective, context, constraints, audience, and deliverables

Acceptance criteria:
- raw input is always converted into a structured specification
- required fields are enforced
- missing fields are tracked explicitly

### Phase 2: Clarification and missing-info engine

Goal:
Ask only for the information that materially affects execution.

Deliverables:
- missing-fact scoring
- clarification ranking
- assumption labeling
- placeholder support for unresolved values

Acceptance criteria:
- no low-impact questions are surfaced
- missing information is either resolved or clearly labeled
- assumptions remain explicit and not silently treated as facts

### Phase 3: Template library and assembler

Goal:
Compose a complete ready-to-send prompt from the structured spec.

Deliverables:
- common task templates
- output-mode selection logic
- deterministic prompt assembly

Acceptance criteria:
- output includes objective, constraints, deliverables, and acceptance criteria
- final prompt reads as an instruction, not a summary

### Phase 4: Validation and anti-hallucination layer

Goal:
Ensure the final product is faithful, actionable, and evidence-based.

Deliverables:
- unsupported-claim detection
- intent drift detection
- requirement recall checks
- specificity/boilerplate scoring

Acceptance criteria:
- fabricated details are rejected
- no important requirement is dropped silently
- final prompt is materially stronger than the source prompt

### Phase 5: Provider-agnostic enhancement pipeline

Goal:
Keep the enhancement engine independent from any single model vendor.

Deliverables:
- provider adapter interface
- offline deterministic provider
- Groq and extension adapters

Acceptance criteria:
- the enhancement logic is not coupled to Groq internals
- offline mode remains deterministic for testing

### Phase 6: API, CLI, and UI integration

Goal:
Expose the final product cleanly to users.

Deliverables:
- enhanced analysis endpoint
- final prompt preview and editing flow
- export-ready prompt output
- comparison between raw input and enhanced result

Acceptance criteria:
- users can review the final output before sending it
- UI signals clearly distinguish the original prompt from the enhanced prompt

### Phase 7: Benchmarking and release gates

Goal:
Measure prompt quality with real criteria instead of only schema compliance.

Deliverables:
- benchmark dataset across task families
- quality metrics for completeness, specificity, intent retention, and hallucination risk
- CI release gates

Acceptance criteria:
- weak prompts are transformed into materially better prompts
- release fails if quality thresholds regress

## 8. Quality metrics

The project should track specific metrics instead of making vague claims about output quality.

### Core metrics

- requirement coverage
- intent preservation
- unsupported-detail rate
- missing-information handling
- specificity delta
- boilerplate ratio
- task-family classification accuracy
- clarification usefulness
- prompt readiness score

### Release thresholds

- requirement coverage must be high and measurable
- hallucination-risk violations must be zero
- final prompt must be materially more specific than the source
- unresolved constraints must be surfaced explicitly

## 9. Risk register

### Risk: generic rewrite remains too weak

Mitigation:
- require structured prompt assembly
- verify every final prompt against a quality rubric
- benchmark against task-specific cases

### Risk: invented facts are silently added

Mitigation:
- explicit assumption labeling
- no unsupported number, name, or constraint creation
- validator rejects fabricated content

### Risk: prompt becomes too long and bloated

Mitigation:
- enforce section-based composition
- penalize boilerplate without evidence
- prefer concise, evidence-backed instructions

### Risk: provider dependence creeps back in

Mitigation:
- keep prompt-crafting logic in provider-agnostic layer
- format contracts stable across providers
- test offline deterministic provider as the baseline

## 10. Definition of done

PromptEasyAI is ready for release when:

- weak prompts are transformed into complete executable instructions,
- output can be sent to another LLM without extra explanation,
- missing facts are surfaced clearly instead of guessed,
- constraints and acceptance criteria remain intact,
- unsupported assumptions are rejected,
- the pipeline works across providers and test environments,
- benchmark and release gates pass at the required quality bar.

## 11. Immediate next actions

1. Replace the current generic optimizer with a structured PromptSpec pipeline.
2. Implement task-family classification and template selection.
3. Add a missing-information scoring engine with clarification-first behavior.
4. Build the final prompt assembler around objective, context, constraints, deliverables, and acceptance criteria.
5. Add a post-generation validation pass for hallucination risk and requirement retention.
6. Measure quality against benchmark cases before exposing the workflow broadly.

This is the corrected strategic plan for the next stage of PromptEasyAI.
