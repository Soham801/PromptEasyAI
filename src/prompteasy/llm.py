import json
import os
import re
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, Protocol, runtime_checkable

from dotenv import load_dotenv
from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError as GroqAuthenticationError,
    BadRequestError,
    Groq,
    InternalServerError,
    RateLimitError as GroqRateLimitError,
    Timeout as GroqTimeout,
    UnprocessableEntityError,
)


@runtime_checkable
class PromptProvider(Protocol):
    model: str

    def generate(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
    ) -> Any:
        ...


class PromptProviderError(RuntimeError):
    def __init__(self, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class AuthenticationError(PromptProviderError):
    pass


class RateLimitError(PromptProviderError):
    def __init__(self, message: str):
        super().__init__(message, retryable=True)


class TimeoutError(PromptProviderError):
    def __init__(self, message: str):
        super().__init__(message, retryable=True)


class ConnectionError(PromptProviderError):
    def __init__(self, message: str):
        super().__init__(message, retryable=True)


class ServerError(PromptProviderError):
    def __init__(self, message: str):
        super().__init__(message, retryable=True)


class SchemaError(PromptProviderError):
    pass


def normalize_provider_error(exc: Exception) -> PromptProviderError:
    if isinstance(exc, GroqAuthenticationError):
        return AuthenticationError(str(exc))

    if isinstance(exc, GroqRateLimitError):
        return RateLimitError(str(exc))

    if isinstance(exc, (APITimeoutError, GroqTimeout)):
        return TimeoutError(str(exc))

    if isinstance(exc, APIConnectionError):
        return ConnectionError(str(exc))

    if isinstance(exc, (InternalServerError, APIStatusError)):
        status_code = getattr(exc, "status_code", None)
        if status_code is not None and 500 <= status_code <= 599:
            return ServerError(str(exc))

    if isinstance(exc, (BadRequestError, UnprocessableEntityError)):
        return SchemaError(str(exc))

    status_code = getattr(exc, "status_code", None)
    if status_code == 401:
        return AuthenticationError(str(exc))
    if status_code == 429:
        return RateLimitError(str(exc))
    if status_code == 408:
        return TimeoutError(str(exc))
    if status_code is not None and 500 <= status_code <= 599:
        return ServerError(str(exc))

    return PromptProviderError(str(exc))


class GroqProvider:
    """
    Provides access to Groq-hosted language models.
    """

    def __init__(self, model: str = "openai/gpt-oss-20b"):
        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )

        self.client = Groq(api_key=api_key)
        self.model = model

    def generate(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
    ) -> Any:
        try:
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format=response_format,
            )
        except Exception as exc:  # pragma: no cover - normalized in analyzer
            raise normalize_provider_error(exc) from exc


def build_offline_response(prompt: str) -> str:
    prompt_text = prompt.strip() or "prompt"
    ambiguities = _infer_ambiguities(prompt_text)
    missing_information = _infer_missing_information(prompt_text)

    return json.dumps(
        {
            "schema_version": "1.0",
            "original_prompt": prompt,
            "intent": f"Understand {prompt_text}",
            "task": f"Process the user's request: {prompt_text}",
            "context": [],
            "constraints": [],
            "output_requirements": [],
            "ambiguities": ambiguities,
            "missing_information": missing_information,
            "optimization_opportunities": _infer_optimization_opportunities(prompt_text),
            "optimized_prompt": build_offline_optimized_prompt(prompt_text),
        }
    )


def build_offline_optimized_prompt(prompt: str) -> str:
    from .prompt_spec import build_prompt_spec, render_prompt_spec

    raw_prompt = (prompt or "").strip() or "prompt"
    original_match = re.search(
        r"Original prompt:\n(.*?)(?:\n\n|\Z)", raw_prompt, re.DOTALL
    )
    prompt_text = original_match.group(1).strip() if original_match else raw_prompt
    question_first = (
        "question-first" in raw_prompt.lower()
        or "clarif" in raw_prompt.lower()
        or "missing details" in raw_prompt.lower()
    )

    spec = build_prompt_spec(prompt_text)
    rendered = render_prompt_spec(spec)

    if question_first:
        return (
            f"{prompt_text}\n\n{rendered}\n\n"
            "Before generating the final answer, ask for the missing details that most affect the result. "
            "Do not assume answers when the user has not provided them."
        )

    return rendered


def _infer_ambiguities(prompt_text: str) -> list[str]:
    lower = prompt_text.lower()
    ambiguities: list[str] = []

    vague_markers = ("best", "better", "improve", "optimize", "good", "quick")
    if any(marker in lower for marker in vague_markers):
        ambiguities.append("The quality target is broad and lacks concrete success criteria.")

    if len(re.findall(r"[a-z0-9']+", lower)) < 8:
        ambiguities.append("The prompt is short and may omit context needed for a precise response.")

    return ambiguities


def _infer_missing_information(prompt_text: str) -> list[str]:
    lower = prompt_text.lower()
    missing: list[str] = []

    if not any(token in lower for token in ("for", "audience", "user", "team", "beginner", "expert")):
        missing.append("Target audience or reader level.")

    if not any(token in lower for token in ("format", "json", "table", "bullets", "steps", "paragraph")):
        missing.append("Preferred output format or structure.")

    if not any(token in lower for token in ("length", "short", "concise", "detailed", "brief")):
        missing.append("Desired response depth or length.")

    return missing


def _infer_optimization_opportunities(prompt_text: str) -> list[str]:
    opportunities = [
        "Specify the intended audience and response depth.",
        "State the preferred output format explicitly.",
        "Include domain constraints and success criteria to reduce ambiguity.",
    ]

    if len(prompt_text.split()) >= 18:
        opportunities.append("Group requirements into explicit sections for objective, constraints, and output style.")

    return opportunities


class OfflineProvider:
    """Simple deterministic provider for tests and local development."""

    def __init__(
        self,
        response: str | Callable[[str], str] | None = None,
        model: str = "offline-model",
    ):
        self.model = model
        self._response = response or build_offline_response

    def generate(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
    ) -> Any:
        user_message = ""
        for item in messages:
            if item.get("role") == "user":
                user_message = item.get("content", "")
                break

        if response_format is None and self._response is build_offline_response:
            response_text = build_offline_optimized_prompt(user_message)
        else:
            response_text = self._response(user_message) if callable(self._response) else self._response

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=response_text)
                )
            ]
        )
