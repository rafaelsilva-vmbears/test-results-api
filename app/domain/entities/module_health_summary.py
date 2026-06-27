""" Represents the health of a specific test module/package. """
from dataclasses import dataclass

@dataclass
class ModuleHealthSummary:
    """ Represents the aggregated health metrics of a test module. """
    module_name: str
    fail_count: int
    total_tests: int
    failure_rate: float
