from __future__ import annotations

from dataclasses import dataclass, field

from .task_classifier import classify_task_family


@dataclass
class PromptSpec:
    objective: str
    task_family: str
    context: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    deliverables: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    output_format: str = ""

    def __post_init__(self) -> None:
        for field_name in ("objective", "task_family", "output_format"):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string.")
            if not value.strip():
                raise ValueError(f"{field_name} cannot be empty.")

        for field_name in (
            "context",
            "constraints",
            "deliverables",
            "acceptance_criteria",
            "assumptions",
        ):
            items = getattr(self, field_name)
            if not isinstance(items, list):
                raise TypeError(f"{field_name} must be a list of strings.")
            for index, item in enumerate(items):
                if not isinstance(item, str):
                    raise TypeError(f"{field_name} item {index} must be a string.")
                if not item.strip():
                    raise ValueError(f"{field_name} item {index} cannot be empty.")


def _build_generic_spec(text: str, task_family: str) -> PromptSpec:
    objective = f"Address the user request: {text}"
    context = [
        "User request: raw prompt supplied for enhancement",
        "Output goal: produce a clearer downstream prompt",
    ]
    constraints = [
        "Preserve the original intent",
        "Do not invent unsupported facts",
        "Keep the final output actionable and concise",
    ]
    deliverables = [
        "Refined task definition",
        "Missing-info summary",
        "Ready-to-send prompt",
    ]
    acceptance_criteria = [
        "The final prompt remains faithful to the original request",
        "The result is clearer and more actionable than the source",
        "Any missing data is surfaced explicitly",
    ]
    assumptions = [
        "If the prompt is underspecified, make the missing information explicit instead of guessing.",
    ]
    output_format = "Provide a structured, implementation-ready prompt with objective, constraints, and output requirements."
    return PromptSpec(
        objective=objective,
        task_family=task_family,
        context=context,
        constraints=constraints,
        deliverables=deliverables,
        acceptance_criteria=acceptance_criteria,
        assumptions=assumptions,
        output_format=output_format,
    )


def _build_login_spec() -> PromptSpec:
    return PromptSpec(
        objective="Create a secure, user-friendly login experience for a web application.",
        task_family="build_implement",
        context=[
            "Product type: SaaS product",
            "Platform: web application",
            "Audience: end users signing into an account",
            "Design tone: modern, clear, trust-building",
        ],
        constraints=[
            "Support email and password sign-in",
            "Validate empty and malformed input",
            "Display clear error states and success feedback",
            "Keep the layout responsive on desktop and mobile",
            "Follow accessibility best practices",
        ],
        deliverables=[
            "UI structure",
            "Interaction flow",
            "Validation behavior",
            "Edge-case handling",
        ],
        acceptance_criteria=[
            "A clear and intuitive login flow",
            "Accessible labels, focus states, and contrast",
            "Professional, conversion-friendly layout",
            "Implementation-ready front-end specification",
        ],
        assumptions=[
            "If no technology stack is specified, use a standard modern web-stack approach unless the user provides other requirements.",
        ],
        output_format=(
            "Provide a concise implementation-ready specification with sections for layout, "
            "behavior, validation, and edge cases."
        ),
    )


def _build_dashboard_spec() -> PromptSpec:
    return PromptSpec(
        objective="Create a clear, useful dashboard that presents information effectively and supports user action.",
        task_family="build_implement",
        context=[
            "Platform: web application",
            "Audience: business users or operators",
            "Tone: practical and easy to scan",
        ],
        constraints=[
            "Highlight key information first",
            "Use a clear information hierarchy",
            "Keep the layout readable on desktop and mobile",
        ],
        deliverables=[
            "Dashboard layout",
            "Key metric presentation",
            "Actionable data views",
        ],
        acceptance_criteria=[
            "Readable and prioritized information",
            "Strong UX clarity",
            "Usable across common device sizes",
        ],
        assumptions=[
            "If no users or metrics are specified, use a generic but practical dashboard structure and clearly label assumptions.",
        ],
        output_format="Provide a concise design and implementation brief with layout, workflow, and success criteria.",
    )


def _build_compare_spec(text: str) -> PromptSpec:
    lower = text.lower()
    candidates: list[str] = []
    seen: set[str] = set()
    for token in ("React", "Vue", "Next.js", "Angular", "Tailwind", "Bootstrap"):
        if token.lower() in lower and token.lower() not in seen:
            candidates.append(token)
            seen.add(token.lower())
    if not candidates:
        candidates = ["React", "Vue"]

    return PromptSpec(
        objective=f"Compare the most relevant options for this request: {text}",
        task_family="compare_choose",
        context=[
            f"Comparison target: {', '.join(candidates[:3])}",
            "Decision context: choose the best fit for the user need and constraints",
            "Evaluation criteria: suitability, maintainability, and implementation effort",
        ],
        constraints=[
            "Compare tradeoffs based on evidence and project context",
            "Do not assume hidden requirements or unsupported constraints",
            "Call out the best fit for the stated scenario",
        ],
        deliverables=[
            "Option comparison",
            "Tradeoff analysis",
            "Recommendation summary",
        ],
        acceptance_criteria=[
            "Clear comparison of strengths and weaknesses",
            "Outcome is specific to the described use case",
            "Final recommendation is defensible and explainable",
        ],
        assumptions=[
            "If missing details exist, label them as unresolved assumptions instead of making them facts.",
        ],
        output_format="Provide a concise comparison with a recommendation, tradeoffs, and decision rationale.",
    )


def _build_write_spec(text: str) -> PromptSpec:
    lower = text.lower()
    audience = "target audience" if "audience" not in lower else "specified audience"
    tone = "clear and persuasive" if "tone" not in lower else "the requested tone"
    return PromptSpec(
        objective=f"Draft high-quality written output for the request: {text}",
        task_family="write_create",
        context=[
            f"Audience: {audience}",
            f"Tone: {tone}",
            "Goal: communicate clearly and effectively without unnecessary filler",
        ],
        constraints=[
            "Preserve the core intent of the source request",
            "Use a polished and readable structure",
            "Do not add unsupported facts or claims",
        ],
        deliverables=[
            "Draft copy",
            "Structure and flow",
            "Final polished wording",
        ],
        acceptance_criteria=[
            "Content is clear and audience-appropriate",
            "Message remains faithful to the original brief",
            "The draft is ready to use or refine for production",
        ],
        assumptions=[
            "If audience, tone, or format is unspecified, use a neutral professional default and label the assumption.",
        ],
        output_format="Provide the final written content with clear structure, tone, and concise wording.",
    )


def _build_plan_spec(text: str) -> PromptSpec:
    return PromptSpec(
        objective=f"Develop a clear plan to address the request: {text}",
        task_family="plan_design",
        context=[
            "Goal: turn a broad request into an actionable plan",
            "Output focus: sequence, milestones, and dependencies",
            "Decision lens: practical execution and clarity",
        ],
        constraints=[
            "Prioritize clarity and realistic sequencing",
            "Keep the plan actionable without inventing hidden context",
            "Identify key dependencies or bottlenecks",
        ],
        deliverables=[
            "Roadmap phases",
            "Timeline and milestones",
            "Execution priorities",
        ],
        acceptance_criteria=[
            "The plan is sequenced and actionable",
            "Priority tasks are called out clearly",
            "The outcome is specific enough to implement or discuss",
        ],
        assumptions=[
            "If the plan requires decisions not supplied by the user, mark them as assumptions and keep them explicit.",
        ],
        output_format="Provide a concise plan with phases, priorities, risks, and implementation sequence.",
    )


def _build_debug_spec() -> PromptSpec:
    return PromptSpec(
        objective="Diagnose and resolve the reported issue with a clear root-cause and remediation path.",
        task_family="debug_fix",
        context=[
            "Problem type: bug or failing behavior",
            "Priority: identify root cause before proposing a fix",
            "Environment: keep the solution traceable and implementation-aware",
        ],
        constraints=[
            "Validate the root cause before suggesting a fix",
            "Check validation and state transitions for the failing flow",
            "Do not assume missing configuration or product details without disclosure",
            "Keep the remediation focused and testable",
        ],
        deliverables=[
            "Root-cause analysis",
            "Fix proposal",
            "Verification steps",
        ],
        acceptance_criteria=[
            "The issue is diagnosed with a clear rationale",
            "The proposed fix is specific and testable",
            "Potential edge cases and validation steps are included",
        ],
        assumptions=[
            "If the exact error detail or environment is missing, state the missing facts and proceed conservatively.",
        ],
        output_format="Provide a concise debugging brief with root cause, fix, and verification plan.",
    )


def _build_summary_spec() -> PromptSpec:
    return PromptSpec(
        objective="Summarize the source material into a clear and accurate executive-level overview.",
        task_family="summarize_distill",
        context=[
            "Goal: extract the essential message and key takeaways",
            "Audience: likely executive or decision-maker readers",
            "Format: concise but complete enough to act on",
        ],
        constraints=[
            "Preserve the original meaning",
            "Avoid adding unstated interpretations",
            "Keep the summary concise and decision-oriented",
        ],
        deliverables=[
            "Executive summary",
            "Key insights",
            "Action-oriented takeaways",
        ],
        acceptance_criteria=[
            "The summary captures the main points without distortion",
            "Important decisions or risks are surfaced clearly",
            "The output remains brief and usable for fast review",
        ],
        assumptions=[
            "If the audience or required level of detail is missing, use a concise professional default and signal the assumption.",
        ],
        output_format="Provide a brief summary with headline insights, key facts, and immediate next steps.",
    )


def build_prompt_spec(prompt: str) -> PromptSpec:
    text = (prompt or "").strip() or "prompt"
    lower = text.lower()
    task_family = classify_task_family(text)

    if task_family == "compare_choose":
        return _build_compare_spec(text)

    if task_family == "debug_fix":
        return _build_debug_spec()

    if task_family == "plan_design":
        return _build_plan_spec(text)

    if task_family == "write_create":
        return _build_write_spec(text)

    if task_family == "summarize_distill":
        return _build_summary_spec()

    if "login" in lower or "sign in" in lower:
        return _build_login_spec()

    if "dashboard" in lower:
        return _build_dashboard_spec()

    return _build_generic_spec(text, task_family)


def render_prompt_spec(spec: PromptSpec) -> str:
    lines: list[str] = []
    lines.append("You are helping complete the user's request.")
    lines.append("")
    lines.append("Objective:")
    lines.append(spec.objective)
    lines.append("")
    lines.append("Context:")
    for item in spec.context:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Requirements:")
    for item in spec.constraints:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Deliverables:")
    for item in spec.deliverables:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Acceptance criteria:")
    for item in spec.acceptance_criteria:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Assumptions:")
    if spec.assumptions:
        for item in spec.assumptions:
            lines.append(f"- {item}")
    else:
        lines.append("- No unsupported assumptions were introduced.")
    lines.append("")
    lines.append("Output format:")
    lines.append(spec.output_format)
    return "\n".join(lines)
