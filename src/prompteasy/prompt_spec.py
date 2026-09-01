from __future__ import annotations

from dataclasses import dataclass, field


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


def build_prompt_spec(prompt: str) -> PromptSpec:
    text = (prompt or "").strip() or "prompt"
    lower = text.lower()

    if "login" in lower or "sign in" in lower:
        task_family = "build_implement"
        objective = "Create a secure, user-friendly login experience for a web application."
        context = [
            "Product type: SaaS product",
            "Platform: web application",
            "Audience: end users signing into an account",
            "Design tone: modern, clear, trust-building",
        ]
        constraints = [
            "Support email and password sign-in",
            "Validate empty and malformed input",
            "Display clear error states and success feedback",
            "Keep the layout responsive on desktop and mobile",
            "Follow accessibility best practices",
        ]
        deliverables = [
            "UI structure",
            "Interaction flow",
            "Validation behavior",
            "Edge-case handling",
        ]
        acceptance_criteria = [
            "A clear and intuitive login flow",
            "Accessible labels, focus states, and contrast",
            "Professional, conversion-friendly layout",
            "Implementation-ready front-end specification",
        ]
        assumptions = [
            "If no technology stack is specified, use a standard modern web-stack approach unless the user provides other requirements.",
        ]
        output_format = (
            "Provide a concise implementation-ready specification with sections for layout, "
            "behavior, validation, and edge cases."
        )
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

    if "dashboard" in lower:
        task_family = "build_implement"
        objective = "Create a clear, useful dashboard that presents information effectively and supports user action."
        context = [
            "Platform: web application",
            "Audience: business users or operators",
            "Tone: practical and easy to scan",
        ]
        constraints = [
            "Highlight key information first",
            "Use a clear information hierarchy",
            "Keep the layout readable on desktop and mobile",
        ]
        deliverables = [
            "Dashboard layout",
            "Key metric presentation",
            "Actionable data views",
        ]
        acceptance_criteria = [
            "Readable and prioritized information",
            "Strong UX clarity",
            "Usable across common device sizes",
        ]
        assumptions = [
            "If no users or metrics are specified, use a generic but practical dashboard structure and clearly label assumptions.",
        ]
        output_format = "Provide a concise design and implementation brief with layout, workflow, and success criteria."
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

    task_family = "analyze_evaluate"
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
