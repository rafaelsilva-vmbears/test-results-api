""" Represents a summary of a common error across test executions. """

from dataclasses import dataclass
from typing import List

@dataclass
class CommonErrorSummary:
    """ Represents a common error across test executions. """
    message: str
    count: int
    affected_tests: List[str]
    affected_runs: List[int]
