from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class FailedTestSummary:
    """
    Value Object representing a summary of a failing test case across multiple runs.
    """
    name: str
    run_numbers: List[int]
    last_message: str
