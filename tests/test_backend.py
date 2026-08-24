from fastapi.testclient import TestClient

from prompteasy.service import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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


def test_analyze_endpoint_returns_valid_analysis():
    response = client.post("/api/analyze", json={"prompt": "Explain machine learning"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["original_prompt"] == "Explain machine learning"
    assert payload["schema_version"] == "1.0"


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
