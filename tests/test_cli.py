import json

from prompteasy.api import analyze_prompt, evaluate_prompt
from prompteasy.cli import main


def test_analyze_prompt_returns_serializable_result():
    result = analyze_prompt("Explain machine learning")

    assert result.original_prompt == "Explain machine learning"
    assert result.schema_version == "1.0"
    assert isinstance(result.model_dump(), dict)


def test_evaluate_prompt_returns_result_for_valid_analysis():
    analysis = analyze_prompt("Explain machine learning")
    result = evaluate_prompt(analysis)

    assert result.valid is True
    assert result.errors == []


def test_cli_analyze_accepts_text_input(capsys):
    exit_code = main(["analyze", "--text", "Explain machine learning"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["original_prompt"] == "Explain machine learning"


def test_cli_config_prints_provider_details(capsys):
    exit_code = main(["config", "--provider", "offline", "--model", "offline-model"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "offline" in captured.out.lower()
    assert "offline-model" in captured.out.lower()
