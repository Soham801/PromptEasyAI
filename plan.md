# PromptEasyAI Delivery Plan

## 1. Root cause and product correction

The current repository is helpful as a prompt-analysis foundation, but the existing optimizer is not yet a true AI prompt enhancer.

The core problem is visible in the current offline behavior. When the system is asked to improve a basic request like:

```text
Build a login page for a SaaS product
```

it returns a generic sentence instead of a complete, send-ready prompt:

```text
Build a login page for a SaaS product. Be accurate. Ask for missing details. State assumptions. Follow user constraints and format.
```

This is not enough for real-world usage. It does not define:

- the product goal,
- the target user,
- screen requirements,
- UX or accessibility requirements,
- edge cases,
- output format,
- acceptance criteria,
- implementation constraints.

A real prompt enhancer must transform a weak request into a structured, actionable downstream instruction that can be sent to any LLM without extra explanation.

## 2. Product definition: AI prompt enhancer

PromptEasyAI should become a model-agnostic prompt compiler that turns a vague user instruction into an implementation-ready, send-to-any-LLM prompt.

The end-user experience should behave like this:

```text
User gives a rough idea
        |
        v
PromptEasyAI extracts task, context, target, constraints, and output needs
        |
        v
PromptEasyAI asks only the critical missing questions when needed
        |
        v
PromptEasyAI assembles a full prompt with objective, context, constraints, deliverables, acceptance criteria, and assumptions
        |
        v
User sends the result to any downstream LLM with minimal follow-up
```

This is not a general chatbot. It is a prompt prep and optimization system.

## 3. Product principles

1. Preserve the user's original intent.
2. Do not invent facts, numbers, product details, or constraints.
3. Make missing information explicit instead of silently guessing.
4. Convert weak instructions into structured action plans.
5. Output a prompt that is ready to send to another model.
6. Keep the system provider-agnostic.
7. Validate the quality of the final prompt, not just the schema.

## 4. Target capability

The final output should be a prompt like this:

```text
You are helping build a SaaS login experience.

Objective:
Create a modern, secure login page for a web application.

Context:
- Product type: SaaS app
- Target users: end users signing into an account
- Platform: web application
- Design tone: modern, clean, trustworthy

Requirements:
- Support email and password sign in
- Include validation for empty and invalid fields
- Show clear error states and success feedback
- Keep the layout responsive on desktop and mobile
- Follow accessibility best practices

Deliverables:
- UI layout
- interaction behavior
- error handling states
- implementation-ready front-end guidance

Acceptance criteria:
- Clean, conversion-focused design
- Easy sign-in flow
- Accessible labels, focus states, and contrast
- No hidden assumptions or fabricated product details

Assumptions:
- If the tech stack is not provided, use a standard web front-end approach unless the user specifies otherwise.

Output format:
Provide a concise implementation-ready specification with sections for layout, behavior, validation, and edge cases.
```

This is materially better than a rephrased sentence. It is usable immediately.

## 5. Current project baseline

The repository already contains the right building blocks:

- a structured `PromptAnalysis` model,
- a provider abstraction,
- offline deterministic validation,
- a web API and CLI,
- basic optimization tests,
- UI and browser workflow scaffolding.

The missing piece is not infrastructure. The missing piece is prompt-quality depth.

## 6. Corrected roadmap

### Phase 0: Problem reset and product definition

Goal:
Clarify that this project is a prompt enhancer, not a generic chatbot or an analysis-only utility.

Deliverables:
- canonical product statement
- final success definition for send-ready prompts
- benchmark examples for weak vs strong prompt outputs

Acceptance criteria:
- all docs refer to the prompt enhancer goal consistently
- the optimization output is judged by readiness and actionability, not length

### Phase 1: Prompt-spec model

Goal:
Create a structured internal representation of the user's task.

Deliverables:
- fields for objective, context, constraints, audience, deliverables, assumptions, success criteria, and output contract
- schema validation for prompt-spec objects
- conversion from raw text to structured requirements

Acceptance criteria:
- the system can identify objective, missing facts, and required deliverables from raw input
- schema validation is deterministic and testable

### Phase 2: Missing-information and clarification engine

Goal:
Ask only the questions that materially affect the downstream result.

Deliverables:
- missing-fact scoring
- question prioritization
- answer merge back into the prompt spec
- explicit assumption labeling

Acceptance criteria:
- no vague or low-value questions
- only critical clarifying questions are surfaced
- assumptions are labeled and not silently treated as facts

### Phase 3: Prompt assembly engine

Goal:
Build a complete prompt from the structured spec.

Deliverables:
- section-based prompt templates for coding, UX, analysis, research, and general content tasks
- final prompt assembly flow
- deterministic formatting rules

Acceptance criteria:
- final prompt contains objective, context, constraints, deliverables, acceptance criteria, and output format
- final prompt reads like a usable instruction for another LLM

### Phase 4: Validation and anti-hallucination layer

Goal:
Ensure the enhanced prompt remains faithful, actionable, and non-fabricated.

Deliverables:
- checks for unsupported assumptions
- checks for intent drift
- checks for under-specified output
- checks for over-compression and omission of critical requirements

Acceptance criteria:
- the validator rejects vague or fabricated prompt rewrites
- the final output is materially better than the raw input

### Phase 5: Provider-agnostic enhancement pipeline

Goal:
Keep the enhancer decoupled from a vendor-specific model.

Deliverables:
- provider interface for prompt enhancement
- offline deterministic provider for tests
- provider-specific adapters for Groq and other model backends

Acceptance criteria:
- the prompt compiler does not rely on a single model
- the same prompt-spec can be sent through different providers

### Phase 6: API, CLI, and UI upgrade

Goal:
Expose the enhanced result cleanly to users.

Deliverables:
- improved analysis endpoint
- prompt preview and edit flow
- export of ready-to-send prompt
- compare raw vs enhanced prompt display

Acceptance criteria:
- users can review and edit the final prompt before sending
- the workflow feels operational and production-ready

### Phase 7: Quality benchmark and release gates

Goal:
Prove that the prompt enhancer is materially improving prompts.

Deliverables:
- benchmark dataset with weak prompts and target task outputs
- quality scoring for completeness, clarity, actionability, and assumption control
- CI gates that block weak prompt improvements

Acceptance criteria:
- the product raises the prompt quality threshold consistently
- weak prompts are transformed into usable task instructions

## 7. Definition of done

The project is ready for release when:

- raw prompts are transformed into complete, actionable instructions,
- the output is ready to send to another LLM without extra explanation,
- missing information is surfaced clearly,
- constraints and acceptance criteria remain intact,
- no unsupported assumptions are silently invented,
- the same pipeline works across providers and environments.

## 8. Priority next steps

1. Replace the current generic optimizer with a structured prompt-spec pipeline.
2. Build the prompt assembler around objective, context, constraints, deliverables, and acceptance criteria.
3. Add a missing-information scoring engine and a clarification loop.
4. Add quality benchmarks that measure prompt readiness, not just schema validity.
5. Keep the API, CLI, and UI aligned with the prompt enhancer workflow.

This is the corrected plan for the next stage of PromptEasyAI.
- Provider/model changes are tracked with before-after quality diffs.

### Completed In This Phase

- Added a versioned benchmark dataset with 10 cases across simple,
  technical, ambiguous, coding, role-based, long, vague, adversarial,
  domain-heavy, and format-critical categories.
- Added machine-readable metrics for validity, requirement retention,
  ambiguity handling, hallucination risk, and intent/task alignment.
- Added the offline `benchmark` CLI command with release thresholds.
- Verified the offline baseline at `10/10` cases passed, pass rate `1.00`,
  and hallucination risk `0.00`.

### Release Note

All Phase 12 implementation deliverables are complete. Groq comparisons
remain opt-in because they require credentials and network access.

### Phase 12 Validation

`\.venv\Scripts\python -m prompteasy.cli benchmark`

Current offline baseline: `10/10` cases passed, pass rate `1.00`, and
hallucination risk `0.00`. The comparison workflow supports explicit
provider/model pairs and persists JSON artifacts.

## 17. Phase 13: Template-Guided Intent-Preserving Prompt Compiler - Planned

### Why This Phase Exists

User testing found that the optimized result is often generic. The current
optimizer applies one broad rewrite instruction and selects only a coarse
strategy. That can improve wording while failing to capture the user's
actual job, audience, domain, success criteria, or required deliverable.

The goal is not to make every prompt longer. The goal is to produce a
ready-to-use downstream instruction that is specific to the user's request,
faithful to its intent, transparent about missing information, and useful
across model providers. Absolute accuracy cannot be guaranteed by an LLM, so
the implementation must make accuracy measurable and reject or expose
uncertain rewrites rather than silently guessing.

### Research Notes: PromptCowboy

The public PromptCowboy site presents a template-led workflow rather than a
single generic rewrite:

- Users can start from role- and job-oriented prompt templates such as
  meeting-note distillation, data analysis, document summarization, PRDs,
  outreach, proposals, and email writing.
- The prompt workspace exposes a prompt type, model choice, and template
  selection before generation; the landing flow labels these as `Prompt type`,
  `Model`, and `PromptTemplate`.
- The product positions the result as a reusable prompt and provides a
  discoverable library, with sign-in required for saving prompts.
- Its FAQ advertises compatibility with multiple AI tools and workflow
  integrations, while the public FAQ content does not expose the exact
  generation algorithm. These product claims are treated as direction, not
  assumptions about implementation.
- Its security page states that customer prompts are not used to train models
  and that stored data can be deleted. PromptEasyAI should preserve its own
  privacy and retention requirements rather than copying claims without the
  corresponding controls.

### Proposed User Flow

```text
Raw prompt
        |
        v
Intent and risk extraction
        |
        v
Task family + role/audience + output mode selection
        |
        v
High-impact clarification questions or explicit placeholders
        |
        v
Template-guided composition with source requirements mapped into sections
        |
        v
Independent preservation, anti-fabrication, and quality evaluation
        |
        v
Ready-to-use prompt + assumptions/questions + quality signals
```

### Deliverables

1. Extend the internal analysis contract with explicit task family, target
        audience, desired outcome, success criteria, source material, risk level,
        and confidence or evidence links. Keep the public contract backward
        compatible or version it deliberately.
2. Add a small versioned template catalog for common task families, including
        writing, summarization, analysis, coding, planning, comparison, and
        content generation. Templates must define slots and required output
        sections, not invent domain facts.
3. Replace the single-pass rewrite with a bounded compiler pipeline:
        classify -> select template -> fill only evidence-backed slots -> ask the
        highest-impact questions or add labeled placeholders -> compose -> critique
        -> repair. Keep provider calls bounded and provider-agnostic.
4. Preserve a traceable mapping from every original explicit requirement to
        its rendered location in the optimized prompt. Never turn a missing value
        into a plausible-sounding fact.
5. Add output modes for direct execution, clarification-first, and
        template-assisted prompts. The mode must be selected from intent and risk,
        not from generic wording alone.
6. Strengthen evaluation with requirement recall, intent/task agreement,
        unsupported-claim detection, ambiguity coverage, template-slot coverage,
        specificity delta, and a penalty for boilerplate that adds no evidence.
7. Add benchmark cases for representative PromptCowboy-style task families,
        underspecified requests, conflicting constraints, prompt injection in
        source material, and prompts where asking a question is better than
        guessing.
8. Update CLI/API/UI responses to show the optimized prompt separately from
        unresolved questions, assumptions, selected mode, and quality signals.

### Implementation Order

1. Define the versioned template and evidence models with deterministic unit
        tests.
2. Implement task-family classification and slot extraction behind the
        existing optimizer interface.
3. Implement template rendering and clarification-first behavior.
4. Add the independent critique/repair loop and stricter evaluation metrics.
5. Update the offline provider so tests exercise the same compiler stages.
6. Update API, CLI, and UI surfaces only after the core contract is stable.
7. Run the expanded benchmark against offline and opt-in live providers.

### Acceptance Criteria

- For every benchmark case, the optimized prompt contains all explicit user
  requirements or reports the exact unresolved conflict.
- Unsupported facts, numbers, names, tools, and constraints are never added;
  missing high-impact information becomes a question or clearly labeled
  placeholder.
- The selected task family and output mode match the labeled intent at the
  agreed benchmark threshold, with confidence exposed when classification is
  uncertain.
- The result is materially more specific than the source without relying on
  generic boilerplate, measured by a documented specificity and boilerplate
  score.
- Prompt compilation remains bounded, deterministic in offline mode, and
  independent of Groq-specific types.
- The existing regression suite remains green, and the new benchmark includes
  a release gate for intent preservation, requirement retention, and zero
  hallucination-risk violations.

### Planned Validation

From the repository root in PowerShell:

1. `cd C:\PromptEasyAI`
2. Add focused tests for template selection, slot filling, clarification
        behavior, preservation mapping, and anti-fabrication repair.
3. Run `\.venv\Scripts\python -m pytest -q`.
4. Run `\.venv\Scripts\python -m prompteasy.cli benchmark` and compare the
        Phase 12 baseline with the Phase 13 report.

### Current Status And Next Steps

The implementation baseline is green: the full offline suite passes with
`47 passed, 2 skipped`, and the benchmark gate passes all 10 offline cases.
Phase 12 is release-complete for the offline quality gate. The GitHub
Actions workflow runs tests, executes a baseline/candidate comparison, and
uploads the JSON artifact while enforcing the thresholds.

Next execution order:

1. Run comparison artifacts for each intended provider/model configuration.
2. Review benchmark results over one release cycle for quality stability.
3. Start Phase 13 deployment and operations after that review.

## 17. Phase 13: Public Deployment And Operations - In Progress

### Goal

Deploy only after optimization quality is stable and measurable.

### Deliverables

- Production configuration, secret management, and environment validation.
- Persistent storage with migrations and backups.
- Authentication, authorization, quotas, and cost controls.
- Monitoring, log shipping, rollback playbooks, and incident response.
- Security and prompt-injection hardening with pre-release validation.

### Completed In This Phase

- Added validated runtime settings for environment, provider, model, and rate limit.
- Wired the FastAPI service to the configured provider instead of forcing offline mode.
- Added production protection that rejects the offline provider.
- Added a production `Dockerfile` and `.dockerignore`.
- Added focused configuration and health endpoint tests.
- Added SQLite-backed history and preferences storage with schema initialization.
- Added optional bearer authentication and per-user record isolation for persistence endpoints.
- Added regression coverage for unauthorized access and cross-user history isolation.
- Updated the security checklist with production configuration requirements.

### Remaining Deliverables

- Add migrations, backups, restore testing, and managed database operations.
- Add authentication, authorization, quotas, and external rate limiting.
- Add managed secrets, HTTPS, monitoring, alerting, rollback procedures, and vulnerability scanning.
- Complete load testing and prompt-injection/data-isolation validation.

### Acceptance Criteria

- Deployment is reproducible and secure.
- User data and credentials are protected.
- Operators can monitor quality, reliability, and cost in production.

### Verified Phase 13A Result

- Focused persistence and configuration checks: `13 passed`.
- Full offline regression: `47 passed, 2 skipped`.
- Offline benchmark: `10/10` passed, pass rate `1.00`, hallucination risk `0.00`.

## 18. Updated Delivery Order

From this point onward, delivery should prioritize quality outcomes over feature breadth:

1. Add authenticated persistence and data isolation.
2. Add managed secrets, HTTPS ingress, quotas, monitoring, and rollback controls.
3. Run security, load, and provider-cost validation.
4. Deploy only after those controls pass a release review.

## 19. Updated Definition Of Done

PromptEasyAI is release-ready when:

- Every user entry point returns a materially improved optimized prompt.
- The optimized prompt preserves intent, constraints, and output requirements.
- Benchmark quality metrics meet documented thresholds across target prompt categories.
- Offline deterministic tests and provider-backed tests both pass their release gates.
- Deployment controls, observability, and security checks are complete.
