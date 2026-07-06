"""This module defines data structures using Pydantic for API request and response schemas."""

from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class MetricsSummaryResponseSchema(BaseModel):
    """Represents a summary of test metrics, including project, /
    environment, total runs/tests, average pass rate/failures, /
    last run number, and last execution date."""

    project: str
    environment: str
    total_runs: int
    total_tests: int
    total_passes: int
    total_failures: int
    total_skipped: int
    avg_pass_rate: float
    avg_failures: float
    avg_skipped: float
    last_run_number: int
    last_execution_date: Optional[datetime] = None
    global_flakiness_rate: float = 0.0

class FailureItemSchema(BaseModel):
    """Represents a failure item, containing the name of the failed test, /
    a list of run numbers where it failed, and the last failure message."""

    name: str
    run_numbers: List[int]
    last_message: str

class CommonErrorItemSchema(BaseModel):
    """Represents a common error category, containing the error message, /
    the frequency of occurrence, and lists of affected tests and runs."""

    message: str
    count: int
    affected_tests: List[str]
    affected_runs: List[int]

class ErrorResponseSchema(BaseModel):
    """Defines a schema for error responses, /
    including error type, message, status code, timestamp, and path."""

    error: Dict[str, str] = Field(
        ...,
        json_schema_extra={
            "example": {
                "type": "ValidationError",
                "message": "Campo 'project' \u00e9 obrigat\u00f3rio.",
                "status_code": 400,
                "timestamp": "2025-10-13T12:44:22Z",
                "path": "/executions"
            }
        }
    )

class ModuleHealthItemSchema(BaseModel):
    """Represents the aggregated health metrics of a test module."""
    module_name: str
    fail_count: int
    total_tests: int = 0
    failure_rate: float = 0.0

class FlakyTestItemSchema(BaseModel):
    """Represents a test that is unstable (fails occasionally)."""
    test_name: str
    fail_count: int
    instability_score: float

class TrendItemSchema(BaseModel):
    """Represents test trends grouped by date."""
    date: str
    total_runs: int
    total_tests: int
    avg_pass_rate: float
    total_failures: int
    total_skipped: int = 0

class MTTRSummarySchema(BaseModel):
    """Represents the Mean Time To Recovery for broken tests."""
    project: str
    environment: str
    mttr_hours: float
    total_recoveries: int

class SlowestTestSchema(BaseModel):
    """Represents a test and its average execution duration."""
    test_name: str
    avg_duration_seconds: float

class PerformanceMetricsSchema(BaseModel):
    """Represents the performance metrics of the test suite."""
    project: str
    environment: str
    avg_execution_time_seconds: float
    slowest_tests: List[SlowestTestSchema]

class StableTestItemSchema(BaseModel):
    """Represents a test that is highly stable."""
    test_name: str
    total_executions: int
    passed_count: int
    pass_rate: float

