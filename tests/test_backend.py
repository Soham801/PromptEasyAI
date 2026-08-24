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
