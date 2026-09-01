# PromptEasyAI Delivery Plan

## 1. Executive summary

PromptEasyAI is currently a solid prompt-analysis foundation, but it is not yet a strong AI prompt enhancer. The project has the right architectural building blocks: structured analysis, provider abstraction, validation, CLI/API entry points, and a working offline test harness. The missing piece is quality depth in the optimization layer.

The verified current output shows the problem clearly:

```powershell
.\.venv\Scripts\python -c "from prompteasy import PromptAnalyzer; from prompteasy.llm import OfflineProvider; a = PromptAnalyzer(provider=OfflineProvider()).analyze('Build a login page for a SaaS product'); print(a.optimized_prompt)"
```

Observed result:

```text
Build a login page for a SaaS product. Be accurate. Ask for missing details. State assumptions. Follow user constraints and format.
```

This is not a production-ready prompt for a downstream LLM. It is generic boilerplate, not a complete task specification. It does not define the actual goal, audience, UI requirements, validation criteria, constraints, or final output contract.

The product must evolve from a prompt rewriter into a prompt compiler: a system that transforms a rough user idea into a complete, implementation-ready instruction that can be sent to another LLM without requiring more explanation.

## 2. Product direction

### 2.1 Product north star

PromptEasyAI should become a model-agnostic prompt enhancement engine whose primary job is:

- understand the user’s intent,
- identify missing facts and risk,
- convert weak input into a fully structured instruction,
- preserve original intent and constraints,
- produce a prompt that is immediately usable by a downstream model.

### 2.2 Scope boundaries

This is not a general-purpose chatbot or autonomous agent. It is not meant to solve the user’s task directly. It exists to produce a higher-quality instruction for another model.

The system should:

- preserve user intent,
- avoid unsupported assumptions,
- surface missing information explicitly,
- assemble a task-ready prompt with structure and acceptance criteria,
- remain provider-agnostic.

## 3. Root cause analysis

### 3.1 What the current system does well

The repository already demonstrates a solid baseline in:

- schema-driven analysis,
- provider abstraction,
- offline deterministic validation,
- CLI and API integration,
- UI workflow scaffolding,
- quality-evaluation infrastructure.

### 3.2 What is still missing

The optimizer currently performs a shallow rewrite. It does not produce a prompt that is rich enough to be used as a final instruction for downstream execution. In practice, the result lacks:

- objective specification,
- audience and context definition,
- constraints and non-functional requirements,
- acceptance criteria,
- edge cases,
- explicit assumptions or clarification requests,
- a clear output contract.

### 3.3 Conclusion

The architecture is correct in shape, but the transformation logic is underpowered. The system needs to move from rephrasing to structured prompt construction.

## 4. Correct design target

The final output should be a prompt like this:

```text
You are helping build a modern SaaS login experience.

Objective:
Create a secure and user-friendly login page for a web application.

Context:
- Product type: SaaS product
- Target users: end users signing into an existing account
- Platform: web app
- Design tone: modern, clean, trustworthy

Requirements:
- Support email and password sign-in
- Validate empty and malformed input
- Display clear error states and success feedback
- Keep the layout responsive on desktop and mobile
- Follow accessibility best practices

Deliverables:
- UI structure
- interaction behavior
- validation logic
- edge-case handling

Acceptance criteria:
- Clear and intuitive flow
- Accessible form controls and focus states
- Professional visual treatment
- Ready for front-end implementation

Assumptions:
- If the technology stack is not specified, use a standard modern web-stack approach unless the user provides a different requirement.

Output format:
Provide a concise, implementation-ready specification with sections for layout, behavior, validation, and edge cases.
```

This is materially better than a generic sentence. It is usable immediately by another model.

## 5. Research-backed direction

### 5.1 Prompt engineering principle

Prompt enhancement should be built as a structured generation problem, not as a single-pass rewrite problem. The system should explicitly compile:

- task goal,
- context,
- constraints,
- success criteria,
- deliverables,
- assumptions,
- unresolved questions,
- output format.

### 5.2 Research direction

The product should borrow from the best practices used in high-quality prompt engineering workflows:

- classify task type,
- identify user role/audience,
- determine output mode,
- separate explicit facts from missing facts,
- ask only high-impact clarifying questions,
- build reusable prompt templates,
- validate final output for faithfulness and completeness.

This is closer to a prompt compiler or prompt-assembly system than to a text paraphraser.

## 6. Required architecture

### 6.1 PromptSpec model

Introduce a structured internal object that captures:

- objective
- task family
- context
- constraints
- audience
- deliverables
- assumptions
- unresolved questions
- success criteria
- output contract
- confidence score

This model should be versioned and validated deterministically.

### 6.2 Task classifier

Add a task classifier that maps raw input into categories such as:

- build/implement
- analyze/evaluate
- write/create
- summarize/condense
- compare/choose
- plan/design
- debug/fix

This classification drives template selection and output mode.

### 6.3 Missing information engine

The engine should detect and score missing facts by impact:

- user audience
- platform
- quality bar
- constraints
- desired output format
- required evidence/sources
- success metrics

Only the highest-impact facts should trigger clarifying questions. Everything else should remain explicit as an assumption or placeholder.

### 6.4 Template catalog

Create a small but explicit template library for common task families:

- coding tasks
- product design tasks
- analysis tasks
- research tasks
- writing tasks
- planning tasks
- comparison tasks

Each template defines required sections and output conventions without inventing unsupported details.

### 6.5 Prompt assembler

The assembler should stitch the final prompt using a fixed schema:

1. Objective
2. Context
3. Requirements and constraints
4. Deliverables
5. Acceptance criteria
6. Assumptions or unresolved questions
7. Final output format

This step should be deterministic and provider-agnostic.

### 6.6 Validation layer

Add a strong final validation stage that checks:

- intent preservation,
- requirement coverage,
- absence of unsupported details,
- clarity and actionability,
- output-specific completeness,
- prompt not over-compressed,
- no invented facts or fabricated constraints.

This validation should be detached from the provider and should evaluate the final prompt itself.

### 6.7 Provider abstraction

The prompt enhancement core should be independent of any single model provider. Provider adapters should be interchangeable and the same internal prompt-spec should be usable across:

- Groq
- OpenAI-compatible providers
- local/offline providers
- future custom providers

## 7. Delivery roadmap

### Phase 0: Product reset and quality definition

Goal:
Align the project around prompt enhancement as the primary mission.

Deliverables:
- clear product statement
- measurable definition of a high-quality optimized prompt
- benchmark examples of weak vs strong output

Acceptance criteria:
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
