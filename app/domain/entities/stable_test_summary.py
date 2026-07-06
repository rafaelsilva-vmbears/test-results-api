from dataclasses import dataclass

@dataclass
class StableTestSummary:
    """Represents a stable test case summary."""
    test_name: str
    total_executions: int
    passed_count: int
    pass_rate: float
