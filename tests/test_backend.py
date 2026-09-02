import pytest
from fastapi.testclient import TestClient

import prompteasy.service as service
from prompteasy.config import Settings
from prompteasy.storage import Storage
from prompteasy.service import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "prompteasyai"
    assert response.json()["environment"] == "development"
    assert response.headers["X-Request-ID"]


def test_metrics_endpoint_reports_requests():
    response = client.get("/api/metrics")

    assert response.status_code == 200
    assert response.json()["requests"]["requests"] >= 1
    assert response.json()["methods"]["GET"] >= 1


def test_root_page_serves_ui():
    response = client.get("/")

    assert response.status_code == 200
    assert "PromptEasyAI" in response.text
    assert "Analyze" in response.text
    assert "Copy optimized prompt" in response.text
    assert "Reset" in response.text
    assert "Export JSON" in response.text
    assert "Useful" in response.text
    assert "Needs work" in response.text
    assert 'id="optimized-editor"' in response.text
    assert "Validated for intent and unsupported details" in response.text
    assert "aria-live=\"polite\"" in response.text


def test_analyze_endpoint_returns_valid_analysis():
    response = client.post("/api/analyze", json={"prompt": "Explain machine learning"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["original_prompt"] == "Explain machine learning"
    assert payload["schema_version"] == "1.0"


def test_analyze_endpoint_rejects_empty_prompt_cleanly():
    response = client.post("/api/analyze", json={"prompt": "   "})

    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_evaluate_endpoint_accepts_analysis_payload():
    response = client.post(
        "/api/evaluate",
        json={
            "analysis": {
                "schema_version": "1.0",
                "original_prompt": "Explain machine learning",
                "intent": "Understand machine learning",
                "task": "Explain machine learning",
                "context": [],
                "constraints": [],
                "output_requirements": [],
                "ambiguities": [],
                "missing_information": [],
                "optimization_opportunities": [],
                "optimized_prompt": "Explain machine learning in clear beginner-friendly terms.",
            }
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["errors"] == []


def test_config_endpoint_returns_provider_settings():
    response = client.get("/api/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "offline"
    assert payload["model"] == "offline-model"


def test_history_endpoint_saves_analysis_entries():
    analysis = {
        "schema_version": "1.0",
        "original_prompt": "Explain machine learning",
        "intent": "Understand machine learning",
        "task": "Explain machine learning",
        "context": [],
        "constraints": [],
        "output_requirements": [],
        "ambiguities": [],
        "missing_information": [],
        "optimization_opportunities": [],
        "optimized_prompt": "Explain machine learning in beginner-friendly language.",
    }

    save_response = client.post(
        "/api/history",
        json={"analysis": analysis, "label": "machine learning"},
    )
    assert save_response.status_code == 200
    saved_payload = save_response.json()
    assert saved_payload["count"] >= 1

    list_response = client.get("/api/history")
    assert list_response.status_code == 200
    history_payload = list_response.json()
    assert len(history_payload["items"]) >= 1
    assert history_payload["items"][0]["label"] == "machine learning"


def test_preferences_endpoint_updates_personalization():
    response = client.post(
        "/api/preferences",
        json={"tone": "friendly", "audience": "beginner", "domain": "education"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["tone"] == "friendly"
    assert payload["audience"] == "beginner"
    assert payload["domain"] == "education"


def test_storage_backup_and_restore_preserve_history_and_preferences(tmp_path):
    database_path = tmp_path / "prompteasy.db"
    backup_path = tmp_path / "backups" / "prompteasy-backup.db"
    storage = Storage(str(database_path))

    storage.save_history("alice", "entry", "2026-09-02T00:00:00Z", {"prompt": "Explain testing"})
    storage.update_preferences("alice", {"tone": "friendly"})
    storage.backup_to(str(backup_path))

    storage.update_preferences("alice", {"tone": "formal"})
    storage.restore_from(str(backup_path))

    assert storage.list_history("alice")[0]["label"] == "entry"
    assert storage.get_preferences("alice")["tone"] == "friendly"


def test_storage_backup_and_restore_reject_invalid_paths(tmp_path):
    database_path = tmp_path / "prompteasy.db"
    storage = Storage(str(database_path))

    with pytest.raises(ValueError, match="differ"):
        storage.backup_to(str(database_path))
    with pytest.raises(FileNotFoundError, match="does not exist"):
        storage.restore_from(str(tmp_path / "missing.db"))


def test_authenticated_storage_isolated_by_user(tmp_path, monkeypatch):
    original_storage = service._storage
    original_get_settings = service.get_settings
    service._storage = Storage(str(tmp_path / "prompteasy.db"))
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: Settings("test", "offline", "offline-model", 60, ":memory:", "shared-secret"),
    )
    try:
        user_a = {"Authorization": "Bearer alice.shared-secret"}
        user_b = {"Authorization": "Bearer bob.shared-secret"}
        unauthorized = client.get("/api/history")
        assert unauthorized.status_code == 401

        analysis = {
            "schema_version": "1.0",
            "original_prompt": "Explain testing",
            "intent": "Learn testing",
            "task": "Explain testing",
            "context": [],
            "constraints": [],
            "output_requirements": [],
            "ambiguities": [],
            "missing_information": [],
            "optimization_opportunities": [],
            "optimized_prompt": "Explain software testing clearly.",
        }
        response = client.post(
            "/api/history",
            headers=user_a,
            json={"analysis": analysis, "label": "alice entry"},
        )
        assert response.status_code == 200
        assert len(client.get("/api/history", headers=user_a).json()["items"]) == 1
        assert client.get("/api/history", headers=user_b).json()["items"] == []
    finally:
        service._storage = original_storage
        service.get_settings = original_get_settings
