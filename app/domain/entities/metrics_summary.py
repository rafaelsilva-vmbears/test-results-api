"""
Value Object representing the summary of project metrics.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class MetricsSummary:
    """Immutable Value Object for Metrics Summary."""
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
    last_execution_date: Optional[datetime]
    global_flakiness_rate: float = 0.0
