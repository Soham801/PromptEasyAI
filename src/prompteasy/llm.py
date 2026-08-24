import json
import os
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
        return RateLimitError(str(exc), retryable=True)

    if isinstance(exc, (APITimeoutError, GroqTimeout)):
        return TimeoutError(str(exc), retryable=True)

    if isinstance(exc, APIConnectionError):
        return ConnectionError(str(exc), retryable=True)

    if isinstance(exc, (InternalServerError, APIStatusError)):
        status_code = getattr(exc, "status_code", None)
        if status_code is not None and 500 <= status_code <= 599:
            return ServerError(str(exc), retryable=True)

    if isinstance(exc, (BadRequestError, UnprocessableEntityError)):
        return SchemaError(str(exc))

    status_code = getattr(exc, "status_code", None)
    if status_code == 401:
        return AuthenticationError(str(exc))
    if status_code == 429:
        return RateLimitError(str(exc), retryable=True)
    if status_code == 408:
        return TimeoutError(str(exc), retryable=True)
    if status_code is not None and 500 <= status_code <= 599:
        return ServerError(str(exc), retryable=True)

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
    ending = "" if prompt_text.endswith((".", "!", "?")) else "."
    return json.dumps(
        {
            "schema_version": "1.0",
            "original_prompt": prompt,
            "intent": f"Understand {prompt_text}",
            "task": f"Process the user's request: {prompt_text}",
            "context": [],
            "constraints": [],
            "output_requirements": [],
            "ambiguities": [],
            "missing_information": [],
            "optimization_opportunities": ["Clarify the audience and desired output."],
            "optimized_prompt": f"{prompt_text}{ending} Provide a clear, direct, and well-structured response.",
        }
    )


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

        response_text = self._response(user_message) if callable(self._response) else self._response
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=response_text)
                )
            ]
        )
