""" Represents a flaky test metric. """
from dataclasses import dataclass

@dataclass
class FlakyTestSummary:
    """ Represents a test that is unstable (fails occasionally). """
    test_name: str
    fail_count: int
    instability_score: float
