import pytest

from prompteasy.config import Settings


def test_settings_default_to_offline_development(monkeypatch):
    monkeypatch.delenv("PROMPTEASY_ENV", raising=False)
    monkeypatch.delenv("PROMPTEASY_PROVIDER", raising=False)
    monkeypatch.delenv("PROMPTEASY_MODEL", raising=False)
    monkeypatch.delenv("PROMPTEASY_RATE_LIMIT", raising=False)

    settings = Settings.from_env()

    assert settings.environment == "development"
    assert settings.provider == "offline"
    assert settings.model == "offline-model"
    assert settings.request_rate_limit == 60


def test_production_rejects_offline_provider(monkeypatch):
    monkeypatch.setenv("PROMPTEASY_ENV", "production")
    monkeypatch.setenv("PROMPTEASY_PROVIDER", "offline")

    with pytest.raises(ValueError, match="offline provider"):
        Settings.from_env()


def test_settings_validate_rate_limit(monkeypatch):
    monkeypatch.setenv("PROMPTEASY_RATE_LIMIT", "0")

    with pytest.raises(ValueError, match="positive integer"):
        Settings.from_env()