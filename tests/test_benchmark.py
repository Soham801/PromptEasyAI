from prompteasy.benchmark import BENCHMARK_THRESHOLD, run_benchmark


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