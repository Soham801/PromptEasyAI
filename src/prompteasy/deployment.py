"""Production deployment configuration and security infrastructure."""

from __future__ import annotations

import os
import logging
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
import hashlib
import hmac


# Configure logging for deployment
def configure_logging(environment: str, log_level: str = "INFO") -> None:
    """Configure structured logging for production deployments.
    
    Args:
        environment: The deployment environment (development, test, production)
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )
    
    if environment == "production":
        # Use JSON format for production log aggregation
        log_format = json.dumps({
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "logger": "%(name)s",
            "message": "%(message)s",
            "file": "%(filename)s",
            "line": "%(lineno)d",
        })
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
        ]
    )


@dataclass(frozen=True)
class SecretsConfig:
    """Configuration for secrets management."""
    
    groq_api_key: Optional[str]
    auth_token: Optional[str]
    db_password: Optional[str]
    jwt_secret: Optional[str]
    
    @classmethod
    def from_env(cls) -> SecretsConfig:
        """Load secrets from environment with secure defaults."""
        return cls(
            groq_api_key=_load_secret("PROMPTEASY_GROQ_API_KEY"),
            auth_token=_load_secret("PROMPTEASY_AUTH_TOKEN"),
            db_password=_load_secret("PROMPTEASY_DB_PASSWORD"),
            jwt_secret=_load_secret("PROMPTEASY_JWT_SECRET"),
        )
    
    def validate_for_production(self) -> list[str]:
        """Validate secrets are properly configured for production.
        
        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []
        
        if not self.groq_api_key:
            errors.append("PROMPTEASY_GROQ_API_KEY is required for production.")
        
        if not self.auth_token:
            errors.append("PROMPTEASY_AUTH_TOKEN is required for production.")
        
        if not self.jwt_secret or len(self.jwt_secret) < 32:
            errors.append(
                "PROMPTEASY_JWT_SECRET must be at least 32 characters for production."
            )
        
        return errors


def _load_secret(key: str) -> Optional[str]:
    """Load a secret from environment or secret file.
    
    Supports two patterns:
    1. Direct environment variable
    2. Secret file path in environment variable (e.g., /run/secrets/key)
    
    Args:
        key: The secret key name
        
    Returns:
        The secret value or None if not found
    """
    # Try direct environment variable
    value = os.getenv(key, "").strip()
    if value:
        return value
    
    # Try secret file pattern (Docker Swarm, Kubernetes)
    secret_path_key = f"{key}_FILE"
    secret_path = os.getenv(secret_path_key, "").strip()
    if secret_path and Path(secret_path).exists():
        try:
            with open(secret_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except (IOError, OSError):
            pass
    
    return None


@dataclass(frozen=True)
class HttpsConfig:
    """Configuration for HTTPS deployment."""
    
    enabled: bool
    cert_path: Optional[str]
    key_path: Optional[str]
    redirect_http: bool
    
    @classmethod
    def from_env(cls) -> HttpsConfig:
        """Load HTTPS configuration from environment."""
        enabled = os.getenv("PROMPTEASY_HTTPS_ENABLED", "false").lower() == "true"
        cert_path = os.getenv("PROMPTEASY_HTTPS_CERT_PATH", "").strip() or None
        key_path = os.getenv("PROMPTEASY_HTTPS_KEY_PATH", "").strip() or None
        redirect_http = os.getenv("PROMPTEASY_HTTPS_REDIRECT", "true").lower() == "true"
        
        return cls(
            enabled=enabled,
            cert_path=cert_path,
            key_path=key_path,
            redirect_http=redirect_http,
        )
    
    def validate(self) -> list[str]:
        """Validate HTTPS configuration.
        
        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []
        
        if self.enabled:
            if not self.cert_path or not Path(self.cert_path).exists():
                errors.append(
                    f"HTTPS enabled but certificate not found at {self.cert_path}"
                )
            
            if not self.key_path or not Path(self.key_path).exists():
                errors.append(
                    f"HTTPS enabled but key not found at {self.key_path}"
                )
        
        return errors


@dataclass(frozen=True)
class QuotasConfig:
    """Configuration for rate limiting and quotas."""
    
    request_rate_limit: int
    requests_per_hour: int
    requests_per_day: int
    max_prompt_length: int
    
    @classmethod
    def from_env(cls) -> QuotasConfig:
        """Load quotas configuration from environment."""
        return cls(
            request_rate_limit=int(os.getenv("PROMPTEASY_RATE_LIMIT", "60")),
            requests_per_hour=int(os.getenv("PROMPTEASY_REQUESTS_PER_HOUR", "1000")),
            requests_per_day=int(os.getenv("PROMPTEASY_REQUESTS_PER_DAY", "10000")),
            max_prompt_length=int(os.getenv("PROMPTEASY_MAX_PROMPT_LENGTH", "50000")),
        )


@dataclass(frozen=True)
class MonitoringConfig:
    """Configuration for monitoring and observability."""
    
    metrics_enabled: bool
    traces_enabled: bool
    log_level: str
    health_check_interval: int
    
    @classmethod
    def from_env(cls) -> MonitoringConfig:
        """Load monitoring configuration from environment."""
        return cls(
            metrics_enabled=os.getenv("PROMPTEASY_METRICS_ENABLED", "true").lower() == "true",
            traces_enabled=os.getenv("PROMPTEASY_TRACES_ENABLED", "false").lower() == "true",
            log_level=os.getenv("PROMPTEASY_LOG_LEVEL", "INFO").upper(),
            health_check_interval=int(os.getenv("PROMPTEASY_HEALTH_CHECK_INTERVAL", "30")),
        )


class SecurityValidator:
    """Security validation and scanning utilities."""
    
    @staticmethod
    def validate_prompt_injection_risk(prompt: str) -> dict[str, Any]:
        """Analyze prompt for common injection attack patterns.
        
        Args:
            prompt: The prompt to analyze
            
        Returns:
            Dictionary with risk assessment
        """
        risk_patterns = [
            "ignore previous instructions",
            "system prompt",
            "jailbreak",
            "ignore all previous",
            "pretend you are",
            "act as if you are",
        ]
        
        prompt_lower = prompt.lower()
        risks_found = [p for p in risk_patterns if p in prompt_lower]
        
        return {
            "safe": len(risks_found) == 0,
            "risk_level": "high" if len(risks_found) > 1 else "medium" if risks_found else "low",
            "patterns_found": risks_found,
            "recommendation": (
                "Block or review this prompt before processing" 
                if len(risks_found) > 1 
                else "Review with caution" if risks_found 
                else "Safe to process"
            ),
        }
    
    @staticmethod
    def validate_secrets_in_prompt(prompt: str) -> dict[str, Any]:
        """Check if prompt contains common secrets or credentials.
        
        Args:
            prompt: The prompt to check
            
        Returns:
            Dictionary with findings
        """
        secret_patterns = [
            ("api_key", r"(?i)(api[_-]?key|apikey)[\"':\s=]+[a-zA-Z0-9]{20,}"),
            ("password", r"(?i)(password|passwd|pwd)[\"':\s=]+"),
            ("token", r"(?i)(token|auth)[\"':\s=]+[a-zA-Z0-9]{20,}"),
            ("jwt", r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
            ("aws_key", r"(?i)(AKIA[0-9A-Z]{16})"),
        ]
        
        secrets_found = []
        for name, pattern in secret_patterns:
            import re
            if re.search(pattern, prompt):
                secrets_found.append(name)
        
        return {
            "contains_secrets": len(secrets_found) > 0,
            "types_found": secrets_found,
            "recommendation": (
                "Block: Prompt contains potential secrets" 
                if secrets_found 
                else "No secrets detected"
            ),
        }
    
    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Compute SHA-256 hash of content for integrity checking.
        
        Args:
            content: The content to hash
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    @staticmethod
    def verify_content_signature(
        content: str, signature: str, secret: str
    ) -> bool:
        """Verify HMAC signature of content.
        
        Args:
            content: The content to verify
            signature: The signature to check
            secret: The secret key used for signing
            
        Returns:
            True if signature is valid
        """
        expected = hmac.new(
            secret.encode("utf-8"),
            content.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)


class DeploymentHealthCheck:
    """Deployment health check utilities."""
    
    @staticmethod
    def check_all(config_data: dict[str, Any]) -> dict[str, Any]:
        """Run all deployment health checks.
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            Health check results
        """
        checks = {
            "environment": config_data.get("environment"),
            "storage": DeploymentHealthCheck._check_storage(config_data),
            "secrets": DeploymentHealthCheck._check_secrets(config_data),
            "https": DeploymentHealthCheck._check_https(config_data),
            "quotas": DeploymentHealthCheck._check_quotas(config_data),
        }
        
        overall_healthy = all(
            check.get("healthy", False) 
            for check in checks.values() 
            if isinstance(check, dict)
        )
        
        return {
            "healthy": overall_healthy,
            "checks": checks,
            "timestamp": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo unknown").read().strip(),
        }
    
    @staticmethod
    def _check_storage(config_data: dict[str, Any]) -> dict[str, Any]:
        """Check storage configuration."""
        storage_path = config_data.get("storage_path", "")
        storage_dir = Path(storage_path).parent if storage_path else Path(".")
        
        try:
            is_writable = os.access(storage_dir, os.W_OK)
            return {
                "healthy": is_writable,
                "storage_path": storage_path,
                "writable": is_writable,
            }
        except Exception as e:
            return {
                "healthy": False,
                "storage_path": storage_path,
                "error": str(e),
            }
    
    @staticmethod
    def _check_secrets(config_data: dict[str, Any]) -> dict[str, Any]:
        """Check secrets configuration."""
        environment = config_data.get("environment", "")
        provider = config_data.get("provider", "")
        
        if environment != "production":
            return {"healthy": True, "status": "development mode"}
        
        # In production, check that secrets are configured
        has_auth = bool(config_data.get("auth_token"))
        has_provider_key = provider == "groq" and bool(
            os.getenv("PROMPTEASY_GROQ_API_KEY")
        )
        
        return {
            "healthy": has_auth and (provider == "offline" or has_provider_key),
            "auth_configured": has_auth,
            "provider_key_configured": has_provider_key if provider == "groq" else True,
        }
    
    @staticmethod
    def _check_https(config_data: dict[str, Any]) -> dict[str, Any]:
        """Check HTTPS configuration."""
        environment = config_data.get("environment", "")
        
        if environment != "production":
            return {"healthy": True, "status": "development mode"}
        
        https_config = HttpsConfig.from_env()
        errors = https_config.validate()
        
        return {
            "healthy": len(errors) == 0,
            "enabled": https_config.enabled,
            "errors": errors,
        }
    
    @staticmethod
    def _check_quotas(config_data: dict[str, Any]) -> dict[str, Any]:
        """Check quotas configuration."""
        quotas = QuotasConfig.from_env()
        
        return {
            "healthy": (
                quotas.request_rate_limit > 0 and
                quotas.requests_per_hour > 0 and
                quotas.requests_per_day > 0 and
                quotas.max_prompt_length > 0
            ),
            "rate_limit": quotas.request_rate_limit,
            "per_hour": quotas.requests_per_hour,
            "per_day": quotas.requests_per_day,
            "max_prompt_length": quotas.max_prompt_length,
        }
