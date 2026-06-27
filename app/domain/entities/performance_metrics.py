from dataclasses import dataclass
from typing import List

@dataclass
class SlowestTestSummary:
    test_name: str
    avg_duration_seconds: float

@dataclass
class PerformanceMetricsSummary:
    project: str
    environment: str
    avg_execution_time_seconds: float
    slowest_tests: List[SlowestTestSummary]
