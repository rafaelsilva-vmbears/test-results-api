from dataclasses import dataclass

@dataclass
class TrendSummary:
    date: str
    total_runs: int
    total_tests: int
    avg_pass_rate: float
    total_failures: int
    total_skipped: int
