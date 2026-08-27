from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str
    provider: str
    model: str
    request_rate_limit: int
    storage_path: str
    auth_token: str

    @classmethod
    def from_env(cls) -> "Settings":
        environment = os.getenv("PROMPTEASY_ENV", "development").strip().lower()
        provider = os.getenv("PROMPTEASY_PROVIDER", "offline").strip().lower()
        model = os.getenv(
            "PROMPTEASY_MODEL",
            "openai/gpt-oss-20b" if provider == "groq" else "offline-model",
        ).strip()
        rate_limit_text = os.getenv("PROMPTEASY_RATE_LIMIT", "60").strip()
        storage_path = os.getenv("PROMPTEASY_STORAGE_PATH", "prompteasy.db").strip()
        auth_token = os.getenv("PROMPTEASY_AUTH_TOKEN", "").strip()

        if environment not in {"development", "test", "production"}:
            raise ValueError("PROMPTEASY_ENV must be development, test, or production.")
        if provider not in {"offline", "groq"}:
            raise ValueError("PROMPTEASY_PROVIDER must be offline or groq.")
        if not model:
            raise ValueError("PROMPTEASY_MODEL cannot be empty.")
        try:
            request_rate_limit = int(rate_limit_text)
        except ValueError as exc:
            raise ValueError("PROMPTEASY_RATE_LIMIT must be a positive integer.") from exc
        if request_rate_limit < 1:
            raise ValueError("PROMPTEASY_RATE_LIMIT must be a positive integer.")
        if not storage_path:
            raise ValueError("PROMPTEASY_STORAGE_PATH cannot be empty.")
        if environment == "production" and provider == "offline":
            raise ValueError("The offline provider cannot be used in production.")

        return cls(environment, provider, model, request_rate_limit, storage_path, auth_token)


def get_settings() -> Settings:
    return Settings.from_env()