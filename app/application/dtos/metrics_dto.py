from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class MetricsSummaryDTO:
    """Data Transfer Object for metrics summary."""
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


@dataclass
class FailedTestDTO:
    """Data Transfer Object for failed test items."""
    name: str
    run_numbers: List[int]
    last_message: str
