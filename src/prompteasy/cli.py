from __future__ import annotations
import argparse
import json
import sys
from .api import analyze_prompt, evaluate_prompt, get_provider_config
from .benchmark import compare_benchmarks, run_benchmark, write_report
from .config import get_settings
from .storage import Storage


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PromptEasyAI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a prompt")
    analyze.add_argument("--text", dest="text")
    analyze.add_argument("--file", dest="file_path")

    evaluate = subparsers.add_parser("evaluate", help="Evaluate a prompt analysis")
    evaluate.add_argument("--text", dest="text", required=True)

    config = subparsers.add_parser("config", help="Show default configuration")
    config.add_argument("--provider", default=None)
    config.add_argument("--model", default=None)

    demo = subparsers.add_parser(
        "demo",
        help="Show a human-readable prompt optimization result",
    )
    demo.add_argument("--text", dest="text", required=True)

    benchmark = subparsers.add_parser("benchmark", help="Run the quality benchmark")
    benchmark.add_argument(
        "--compare",
        action="append",
        metavar="PROVIDER:MODEL",
        help="Benchmark a provider/model pair; repeat for candidate comparisons.",
    )
    benchmark.add_argument("--output", help="Write the benchmark report to a JSON file.")

    storage = subparsers.add_parser("storage", help="Back up or restore local storage")
    storage_group = storage.add_mutually_exclusive_group(required=True)
    storage_group.add_argument("--backup", metavar="PATH", help="Write a database backup")
    storage_group.add_argument("--restore", metavar="PATH", help="Restore a database backup")
    storage.add_argument("--database", help="Override the configured database path")

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

        analysis = analyze_prompt(prompt)
        print(json.dumps(analysis.model_dump(mode="json")))
        return 0

    if args.command == "evaluate":
        analysis = analyze_prompt(args.text)
        result = evaluate_prompt(analysis)
        print(json.dumps({
            "valid": result.valid,
            "errors": result.errors,
        }))
        return 0 if result.valid else 1

    if args.command == "config":
        configured = get_provider_config()
        if args.provider:
            configured["provider"] = args.provider
        if args.model:
            configured["model"] = args.model
        print(json.dumps(configured))
        return 0

    if args.command == "demo":
        analysis = analyze_prompt(args.text)
        result = evaluate_prompt(analysis)

        print("PromptEasyAI Verification")
        print("=" * 28)
        print(f"Original prompt: {analysis.original_prompt}")
        print(f"Intent: {analysis.intent}")
        print(f"Task: {analysis.task}")
        print(f"Context: {_format_items(analysis.context)}")
        print(f"Constraints: {_format_items(analysis.constraints)}")
        print(f"Output requirements: {_format_items(analysis.output_requirements)}")
        print(f"Ambiguities: {_format_items(analysis.ambiguities)}")
        print(f"Missing information: {_format_items(analysis.missing_information)}")
        print(
            "Optimization opportunities: "
            + _format_items(analysis.optimization_opportunities)
        )
        print(f"Optimized prompt: {analysis.optimized_prompt}")
        print(f"Validation: {'PASS' if result.valid else 'FAIL'}")
        if result.errors:
            print("Validation errors: " + "; ".join(result.errors))
        return 0 if result.valid else 1

    if args.command == "benchmark":
        if args.compare:
            pairs = []
            for value in args.compare:
                provider, separator, model = value.partition(":")
                if not separator or not provider or not model:
                    parser.error("--compare must use PROVIDER:MODEL")
                pairs.append((provider.lower(), model))
            report = compare_benchmarks(pairs)
        else:
            report = run_benchmark()
        if args.output:
            write_report(report, args.output)
        print(json.dumps(report.to_dict()))
        if hasattr(report, "release_gate_passed"):
            return 0 if report.release_gate_passed else 1
        return 0 if report.baseline["release_gate_passed"] and all(
            candidate["release_gate_passed"] for candidate in report.candidates
        ) else 1

    if args.command == "storage":
        database = args.database or get_settings().storage_path
        storage = Storage(database)
        if args.backup:
            destination = storage.backup_to(args.backup)
            operation = "backup"
        else:
            destination = storage.restore_from(args.restore)
            operation = "restore"
        print(json.dumps({"operation": operation, "database": str(destination)}))
        return 0

    parser.error("Unsupported command")
    return 2


def _format_items(items: list[str]) -> str:
    return ", ".join(items) if items else "none"


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
