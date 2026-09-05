from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from .deployment import (
    SecretsConfig,
    HttpsConfig,
    QuotasConfig,
    MonitoringConfig,
    DeploymentHealthCheck,
)


@dataclass(frozen=True)
class Settings:
    environment: str
    provider: str
    model: str
    request_rate_limit: int
    storage_path: str
    auth_token: str
    
    # Phase 13 deployment features
    secrets: SecretsConfig
    https_config: HttpsConfig
    quotas: QuotasConfig
    monitoring: MonitoringConfig

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

        # Load deployment features
        secrets = SecretsConfig.from_env()
        https_config = HttpsConfig.from_env()
        quotas = QuotasConfig.from_env()
        monitoring = MonitoringConfig.from_env()
        
        # Validate production deployment
        if environment == "production":
            secret_errors = secrets.validate_for_production()
            https_errors = https_config.validate()
            
            if secret_errors:
                raise ValueError(
                    f"Production secrets validation failed: {'; '.join(secret_errors)}"
                )
            
            if https_errors:
                raise ValueError(
                    f"Production HTTPS validation failed: {'; '.join(https_errors)}"
                )

        return cls(
            environment=environment,
            provider=provider,
            model=model,
            request_rate_limit=request_rate_limit,
            storage_path=storage_path,
            auth_token=auth_token,
            secrets=secrets,
            https_config=https_config,
            quotas=quotas,
            monitoring=monitoring,
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert settings to dictionary for API responses."""
        return {
            "environment": self.environment,
            "provider": self.provider,
            "model": self.model,
            "request_rate_limit": self.request_rate_limit,
            "storage_path": self.storage_path,
            "https_enabled": self.https_config.enabled,
            "metrics_enabled": self.monitoring.metrics_enabled,
            "traces_enabled": self.monitoring.traces_enabled,
            "log_level": self.monitoring.log_level,
        }
    
    def get_health_check(self) -> dict[str, Any]:
        """Get comprehensive health check for this configuration."""
        return DeploymentHealthCheck.check_all(self.to_dict())


def get_settings() -> Settings:
    return Settings.from_env()