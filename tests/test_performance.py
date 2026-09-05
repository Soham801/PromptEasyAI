"""Tests for load testing, vulnerability scanning, and performance validation."""

import pytest
from prompteasy.performance import (
    LoadTestResult,
    LoadTester,
    VulnerabilityScanner,
    RollbackManager,
)


class TestLoadTestResult:
    """Test LoadTestResult data class."""
    
    def test_load_test_result_conversion_to_dict(self):
        """Test conversion of LoadTestResult to dictionary."""
        result = LoadTestResult(
            test_name="test_1",
            total_requests=100,
            successful_requests=99,
            failed_requests=1,
            duration_seconds=10.5,
            min_response_time=0.01,
            max_response_time=0.5,
            avg_response_time=0.1,
            median_response_time=0.09,
            p95_response_time=0.2,
            p99_response_time=0.3,
            requests_per_second=9.52,
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["test_name"] == "test_1"
        assert result_dict["total_requests"] == 100
        assert result_dict["successful_requests"] == 99
        assert result_dict["success_rate"] == pytest.approx(0.99)


class TestLoadTester:
    """Test load testing functionality."""
    
    def test_run_concurrent_test_success(self):
        """Test successful concurrent load test."""
        call_count = 0
        
        def test_fn():
            nonlocal call_count
            call_count += 1
        
        result = LoadTester.run_concurrent_test(
            test_fn=test_fn,
            num_concurrent=2,
            num_iterations=10,
            timeout_seconds=5,
        )
        
        assert result.total_requests == 10
        assert result.successful_requests > 0
        assert result.avg_response_time >= 0
        assert result.requests_per_second > 0
    
    def test_run_concurrent_test_with_failures(self):
        """Test concurrent load test with some failures."""
        call_count = 0
        
        def failing_test_fn():
            nonlocal call_count
            call_count += 1
            if call_count % 3 == 0:
                raise ValueError("Simulated failure")
        
        result = LoadTester.run_concurrent_test(
            test_fn=failing_test_fn,
            num_concurrent=2,
            num_iterations=6,
            timeout_seconds=5,
        )
        
        assert result.total_requests == 6
        assert result.failed_requests > 0
        assert result.successful_requests > 0
    
    def test_validate_performance_passes(self):
        """Test performance validation that passes SLA."""
        result = LoadTestResult(
            test_name="test",
            total_requests=100,
            successful_requests=100,
            failed_requests=0,
            duration_seconds=10,
            min_response_time=0.01,
            max_response_time=0.5,
            avg_response_time=0.05,
            median_response_time=0.04,
            p95_response_time=0.1,
            p99_response_time=0.15,
            requests_per_second=10.0,
        )
        
        passed, errors = LoadTester.validate_performance(result)
        
        assert passed is True
        assert len(errors) == 0
    
    def test_validate_performance_fails_avg_response_time(self):
        """Test performance validation failure on average response time."""
        result = LoadTestResult(
            test_name="test",
            total_requests=100,
            successful_requests=100,
            failed_requests=0,
            duration_seconds=10,
            min_response_time=0.5,
            max_response_time=3.0,
            avg_response_time=2.0,  # Exceeds 1.0s limit
            median_response_time=1.5,
            p95_response_time=2.5,
            p99_response_time=3.0,
            requests_per_second=10.0,
        )
        
        passed, errors = LoadTester.validate_performance(result)
        
        assert passed is False
        assert len(errors) > 0
        assert any("Average response time" in e for e in errors)
    
    def test_validate_performance_fails_success_rate(self):
        """Test performance validation failure on success rate."""
        result = LoadTestResult(
            test_name="test",
            total_requests=100,
            successful_requests=80,  # 80% success rate
            failed_requests=20,
            duration_seconds=10,
            min_response_time=0.01,
            max_response_time=0.5,
            avg_response_time=0.05,
            median_response_time=0.04,
            p95_response_time=0.1,
            p99_response_time=0.15,
            requests_per_second=10.0,
        )
        
        passed, errors = LoadTester.validate_performance(result)
        
        assert passed is False
        assert any("Success rate" in e for e in errors)


class TestVulnerabilityScanner:
    """Test vulnerability scanning."""
    
    def test_check_common_vulnerabilities_no_issues(self, monkeypatch):
        """Test vulnerability check with no issues."""
        monkeypatch.delenv("DEBUG", raising=False)
        monkeypatch.setenv("PROMPTEASY_ENV", "development")
        
        result = VulnerabilityScanner.check_common_vulnerabilities()
        
        assert isinstance(result, dict)
        assert "vulnerabilities_found" in result
        assert "issues" in result
        assert "recommendations" in result
    
    def test_check_common_vulnerabilities_debug_enabled(self, monkeypatch):
        """Test vulnerability check with DEBUG enabled."""
        monkeypatch.setenv("DEBUG", "true")
        
        result = VulnerabilityScanner.check_common_vulnerabilities()
        
        assert result["vulnerabilities_found"] > 0
        assert len(result["issues"]) > 0
        assert any("DEBUG" in str(issue) for issue in result["issues"])
    
    def test_check_common_vulnerabilities_production_no_https(self, monkeypatch):
        """Test vulnerability check for production without HTTPS."""
        monkeypatch.setenv("PROMPTEASY_ENV", "production")
        monkeypatch.setenv("PROMPTEASY_HTTPS_ENABLED", "false")
        
        result = VulnerabilityScanner.check_common_vulnerabilities()
        
        assert result["vulnerabilities_found"] > 0
        assert any("HTTPS" in str(issue) for issue in result["issues"])
    
    def test_validate_api_endpoints(self):
        """Test API endpoint validation."""
        result = VulnerabilityScanner.validate_api_endpoints()
        
        assert "total_checks" in result
        assert "passed" in result
        assert "failed" in result
        assert "checks" in result
        assert len(result["checks"]) > 0
    
    def test_validate_dependencies(self):
        """Test dependency vulnerability check."""
        result = VulnerabilityScanner.validate_dependencies()
        
        assert "scan_status" in result
        assert "dependencies_scanned" in result
        assert "vulnerabilities_found" in result
    
    def test_generate_security_report(self):
        """Test comprehensive security report generation."""
        report = VulnerabilityScanner.generate_security_report()
        
        assert "report_type" in report
        assert "timestamp" in report
        assert "common_vulnerabilities" in report
        assert "endpoint_validation" in report
        assert "dependency_check" in report
        assert "summary" in report
        assert report["report_type"] == "deployment_security_assessment"


class TestRollbackManager:
    """Test rollback and recovery utilities."""
    
    def test_create_rollback_checkpoint(self):
        """Test creating a rollback checkpoint."""
        config = {"provider": "groq", "model": "test"}
        data = {"version": 1, "entries": 100}
        
        checkpoint = RollbackManager.create_rollback_checkpoint(
            deployment_id="deploy-123",
            config_snapshot=config,
            data_snapshot=data,
        )
        
        assert checkpoint["deployment_id"] == "deploy-123"
        assert "timestamp" in checkpoint
        assert checkpoint["config_snapshot"] == config
        assert checkpoint["data_snapshot"] == data
        assert checkpoint["status"] == "ready"
    
    def test_validate_rollback_state_success(self):
        """Test successful rollback state validation."""
        checkpoint = {
            "deployment_id": "deploy-123",
            "timestamp": 1234567890,
            "config_snapshot": {"provider": "groq"},
            "data_snapshot": {"version": 1},
            "status": "ready",
        }
        
        valid, errors = RollbackManager.validate_rollback_state(checkpoint)
        
        assert valid is True
        assert len(errors) == 0
    
    def test_validate_rollback_state_missing_fields(self):
        """Test rollback validation with missing fields."""
        checkpoint = {
            "deployment_id": "deploy-123",
            # Missing timestamp, config_snapshot, data_snapshot
            "status": "ready",
        }
        
        valid, errors = RollbackManager.validate_rollback_state(checkpoint)
        
        assert valid is False
        assert len(errors) > 0
    
    def test_validate_rollback_state_invalid_status(self):
        """Test rollback validation with invalid status."""
        checkpoint = {
            "deployment_id": "deploy-123",
            "timestamp": 1234567890,
            "config_snapshot": {"provider": "groq"},
            "data_snapshot": {"version": 1},
            "status": "failed",  # Invalid status
        }
        
        valid, errors = RollbackManager.validate_rollback_state(checkpoint)
        
        assert valid is False
        assert any("status" in str(e).lower() for e in errors)
