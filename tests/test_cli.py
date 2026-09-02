import json

from prompteasy.api import analyze_prompt, evaluate_prompt
from prompteasy.cli import main


def test_analyze_prompt_returns_serializable_result():
    result = analyze_prompt("Explain machine learning")

    assert result.original_prompt == "Explain machine learning"
    assert result.schema_version == "1.0"
    assert isinstance(result.model_dump(), dict)


def test_analyze_prompt_returns_improved_prompt_text():
    result = analyze_prompt("Write a project summary")

    assert result.optimized_prompt != result.original_prompt
    assert "missing details" in result.optimized_prompt.lower()


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


def test_cli_demo_prints_human_readable_verification(capsys):
    exit_code = main(["demo", "--text", "Explain machine learning to a beginner"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "PromptEasyAI Verification" in captured.out
    assert "Original prompt:" in captured.out
    assert "Optimized prompt:" in captured.out
    assert "Validation: PASS" in captured.out


def test_cli_storage_backup_and_restore(tmp_path, capsys):
    database_path = tmp_path / "prompteasy.db"
    backup_path = tmp_path / "backup.db"

    assert main(["storage", "--database", str(database_path), "--backup", str(backup_path)]) == 0
    backup_output = json.loads(capsys.readouterr().out)
    assert backup_output == {"operation": "backup", "database": str(backup_path)}

    assert main(["storage", "--database", str(database_path), "--restore", str(backup_path)]) == 0
    restore_output = json.loads(capsys.readouterr().out)
    assert restore_output == {"operation": "restore", "database": str(database_path)}
