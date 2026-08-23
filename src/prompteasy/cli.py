from __future__ import annotations

import argparse
import json
import sys

from .api import analyze_prompt, evaluate_prompt
from .llm import OfflineProvider


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PromptEasyAI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a prompt")
    analyze.add_argument("--text", dest="text")
    analyze.add_argument("--file", dest="file_path")

    evaluate = subparsers.add_parser("evaluate", help="Evaluate a prompt analysis")
    evaluate.add_argument("--text", dest="text", required=True)

    config = subparsers.add_parser("config", help="Show default configuration")
    config.add_argument("--provider", default="offline")
    config.add_argument("--model", default="offline-model")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        prompt = args.text or ""
        if not prompt and args.file_path:
            with open(args.file_path, "r", encoding="utf-8") as handle:
                prompt = handle.read()
        if not prompt:
            print(json.dumps({"error": "No prompt provided"}))
            return 2

        analysis = analyze_prompt(prompt, provider=OfflineProvider())
        print(json.dumps(analysis.model_dump(mode="json")))
        return 0

    if args.command == "evaluate":
        analysis = analyze_prompt(args.text, provider=OfflineProvider())
        result = evaluate_prompt(analysis)
        print(json.dumps({
            "valid": result.valid,
            "errors": result.errors,
        }))
        return 0 if result.valid else 1

    if args.command == "config":
        print(json.dumps({
            "provider": args.provider,
            "model": args.model,
        }))
        return 0

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
