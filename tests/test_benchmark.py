import json

from prompteasy.benchmark import BENCHMARK_THRESHOLD, compare_benchmarks, run_benchmark, write_report


def test_benchmark_covers_quality_categories_and_metrics():
    report = run_benchmark()

    assert report.dataset_version == "1.0"
    assert report.total >= 10
    assert {"vague", "adversarial", "domain-heavy", "format-critical"} <= {
        case.category for case in report.cases
    }
    assert set(report.metrics) >= {
        "requirement_retention",
        "ambiguity_handling",
        "hallucination_risk",
    }
    assert report.pass_rate >= BENCHMARK_THRESHOLD
    assert report.release_gate_passed is True


def test_benchmark_comparison_tracks_candidate_deltas(tmp_path):
    output = tmp_path / "benchmark.json"
    comparison = compare_benchmarks(
        [("offline", "baseline"), ("offline", "candidate")]
    )
    write_report(comparison, output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["baseline"]["model"] == "baseline"
    assert payload["candidates"][0]["model"] == "candidate"
    assert payload["candidates"][0]["pass_rate_delta"] == 0.0
    assert payload["candidates"][0]["delta"]["hallucination_risk"] == 0.0