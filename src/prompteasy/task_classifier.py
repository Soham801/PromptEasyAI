from __future__ import annotations


def classify_task_family(prompt: str) -> str:
    """Return a stable task-family label for the incoming prompt."""
    if not isinstance(prompt, str):
        raise TypeError("prompt must be a string")

    text = prompt.strip().lower()
    if not text:
        raise ValueError("prompt cannot be empty")

    if any(
        marker in text
        for marker in (
            "compare",
            "vs",
            "versus",
            "choose",
            "which is better",
            "difference between",
            "tradeoff",
        )
    ):
        return "compare_choose"

    if any(
        marker in text
        for marker in (
            "debug",
            "fix",
            "error",
            "issue",
            "bug",
            "troubleshoot",
        )
    ):
        return "debug_fix"

    if any(
        marker in text
        for marker in (
            "plan",
            "roadmap",
            "strategy",
            "approach",
            "timeline",
            "architecture",
        )
    ):
        return "plan_design"

    if any(
        marker in text
        for marker in (
            "write",
            "draft",
            "article",
            "email",
            "blog",
            "copy",
            "script",
        )
    ):
        return "write_create"

    if any(
        marker in text
        for marker in (
            "summarize",
            "summary",
            "condense",
            "distill",
            "tl;dr",
        )
    ):
        return "summarize_distill"

    if any(
        marker in text
        for marker in (
            "build",
            "create",
            "design",
            "implement",
            "make",
            "develop",
            "page",
            "dashboard",
            "login",
            "app",
            "website",
            "ui",
        )
    ):
        return "build_implement"

    if any(
        marker in text
        for marker in (
            "explain",
            "analyze",
            "evaluate",
            "why",
            "breakdown",
            "assess",
            "understand",
        )
    ):
        return "analyze_evaluate"

    return "analyze_evaluate"
