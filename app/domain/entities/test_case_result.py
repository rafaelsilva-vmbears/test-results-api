"""
Consolidated domain entity for test runs with embedded test results.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class TestStatus(str, Enum):
    """Test execution status."""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    SKIPPED = "skipped"
    NOT_FOUND = "not_found"


class TestResultStatus(str, Enum):
    """Individual test result status."""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestCaseResult:
    """
    Represents an individual test case result (embedded).
    Simplified version without separate ID or timestamps.
    """
    # Test identification
    name: str = ""
    classname: Optional[str] = None

    # Result details
    run_number: int = 0
    status: TestResultStatus = TestResultStatus.PASSED
    time: float = 0.0

    # Failure information
    message: Optional[str] = None

    @property
    def is_failure(self) -> bool:
        """Check if test failed (includes error)."""
        return self.status in [TestResultStatus.FAILED, TestResultStatus.ERROR]

    @property
    def full_name(self) -> str:
        """Get full test name with class prefix if available."""
        if self.classname:
            return f"{self.classname} - {self.name}"
        return self.name

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.full_name,  # Persist legacy behavior (Full Name in 'name' field)
            "short_name": self.name, # New field for clarity
            "classname": self.classname,
            "classname": self.classname,
            "run_number": self.run_number,
            "status": self.status.value if isinstance(self.status, TestResultStatus) else self.status,
            "time": self.time,
            "message": self.message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCaseResult":
        """Create from dictionary."""
        data = data.copy()

        # Handle status enum conversion
        if data.get("status") and isinstance(data["status"], str):
            data["status"] = TestResultStatus(data["status"])

        # Consume short_name if present (cleaner name source)
        if "short_name" in data:
            data["name"] = data.pop("short_name")

        return cls(**data)


@dataclass
class ConsolidatedTestRun:
    """
    Consolidated test run entity with embedded test results.

    Note:
        - `failures` is defined as the sum of failures and errors (i.e. all non-passing tests).
        - `error` is kept as a separate field to preserve the detailed count of errors.
    """

    # Identity
    id: Optional[str] = None

    # Core attributes
    build_number: Optional[int] = None
    build_url: Optional[str] = None

    # Execution details
    status: TestStatus = TestStatus.SUCCESS
    total: int = 0
    passed: int = 0
    failures: int = 0   # aggregated: failed + errors
    skipped: int = 0
    error: int = 0    # details: only errors

    # Timing
    time: float = 0.0

    # Source information
    source: str = "jenkins"  # jenkins, s3, local
    source_url: Optional[str] = None

    # **EMBEDDED TEST RESULTS** - Array de testes
    test_results: List[TestCaseResult] = field(default_factory=list)

    # Audit fields
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    execution_date: Optional[datetime] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.created_at is None:
            self.created_at = datetime.now()

        if self.updated_at is None:
            self.updated_at = self.created_at

        # Auto-calculate statistics from test_results if not provided
        if self.test_results and self.total == 0:
            self._calculate_statistics()

    def _calculate_statistics(self):
        """Calculate test statistics from test_results array.

        Sets:
            - total
            - passed
            - error (count of ERROR status)
            - failures (FAILED + ERROR)  <-- aggregated
            - skipped
            - status (overall)
        """
        self.total = len(self.test_results)
        self.passed = sum(
            1 for t in self.test_results if t.status == TestResultStatus.PASSED)
        failures_only = sum(
            1 for t in self.test_results if t.status == TestResultStatus.FAILED)
        errors_only = sum(
            1 for t in self.test_results if t.status == TestResultStatus.ERROR)
        self.error = errors_only
        # Aggregate failures as failures + errors (all non-passing)
        self.failures = failures_only + errors_only
        self.skipped = sum(
            1 for t in self.test_results if t.status == TestResultStatus.SKIPPED)

        # Determine overall status
        if self.failures > 0:
            self.status = TestStatus.FAILURE
        elif self.skipped == self.total and self.total > 0:
            self.status = TestStatus.SKIPPED
        else:
            self.status = TestStatus.SUCCESS

    def add_test_result(self, test_result: TestCaseResult):
        """Add a test result and update statistics."""
        self.test_results.append(test_result)
        self._calculate_statistics()
        self.updated_at = datetime.now()

    @property
    def success_rate(self) -> float:
        """Calculate test success rate."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100

    @property
    def failure_rate(self) -> float:
        """Calculate test failure rate (using aggregated failures)."""
        if self.total == 0:
            return 0.0
        return (self.failures / self.total) * 100

    @property
    def skipped_rate(self) -> float:
        """Calculate test skipped rate."""
        if self.total == 0:
            return 0.0
        return (self.skipped / self.total) * 100

    @property
    def failed_names(self) -> List[str]:
        """Get list of failed test names (includes errors)."""
        return [
            test.full_name for test in self.test_results
            if test.is_failure
        ]

    @property
    def passed_names(self) -> List[str]:
        """Get list of passed test names."""
        return [
            test.full_name for test in self.test_results
            if test.status == TestResultStatus.PASSED
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for persistence."""
        return {
            "id": self.id,
            "build_number": self.build_number,
            "build_url": self.build_url,
            "status": self.status.value if isinstance(self.status, TestStatus) else self.status,
            "total": self.total,
            "passed": self.passed,
            # failures já agrega failures + errors
            "failures": self.failures,
            "error": self.error,
            "skipped": self.skipped,
            "time": self.time,
            "source": self.source,
            "source_url": self.source_url,
            "test_results": [test.to_dict() for test in self.test_results],
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "execution_date": self.execution_date.isoformat() if isinstance(self.execution_date, datetime) else self.execution_date
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConsolidatedTestRun":
        """Create entity from dictionary."""
        # Parse datetime fields
        if data.get("created_at") and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        if data.get("updated_at") and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        if data.get("execution_date") and isinstance(data["execution_date"], str):
            data["execution_date"] = datetime.fromisoformat(data["execution_date"])

        # Parse status enum
        if data.get("status") and isinstance(data["status"], str):
            data["status"] = TestStatus(data["status"])

        # Parse test_results array
        if data.get("test_results"):
            data["test_results"] = [
                TestCaseResult.from_dict(
                    test) if isinstance(test, dict) else test
                for test in data["test_results"]
            ]

        if data.get("time") and isinstance(data["time"], (int, float)):
            data["time"] = float(data["time"])

        return cls(**data)

    def get_tests_by_status(self, status: TestResultStatus) -> List[TestCaseResult]:
        """Get all tests with specific status."""
        return [test for test in self.test_results if test.status == status]

    def get_slowest_tests(self, limit: int = 10) -> List[TestCaseResult]:
        """Get slowest tests."""
        return sorted(
            self.test_results,
            key=lambda t: t.time,
            reverse=True
        )[:limit]

    def summary(self) -> Dict[str, Any]:
        """Get a summary of the test run."""
        # Calculate failures (excluding errors) and errors separately
        failures_only = self.failures - self.error

        # Get failed test cases
        failed_cases = [
            test.to_dict() for test in self.test_results
            if test.status in [TestResultStatus.FAILED, TestResultStatus.ERROR]
        ]

        return {
            "total": self.total,
            "failures": failures_only,
            "passed": self.passed,
            "errors": self.error,
            "skipped": self.skipped,
            "time": self.time,
            "status": self.status.value,
            "source": self.source,
            "pass_rate": round((self.total - self.failures - self.skipped) / self.total * 100, 2) if self.total > 0 else 0,
            "failure_rate": round(self.failures / self.total * 100, 2) if self.total > 0 else 0,
            "skipped_rate": round(self.skipped / self.total * 100, 2) if self.total > 0 else 0,
            "tests": [test.to_dict() for test in self.test_results],
            "failed_cases": failed_cases,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "execution_date": self.execution_date.isoformat() if isinstance(self.execution_date, datetime) else self.execution_date
        }
