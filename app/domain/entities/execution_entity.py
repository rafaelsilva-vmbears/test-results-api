""" Represents an execution run containing metadata and aggregated test results. """

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class TestEntity:
    """ Represents a single test case with its details. """
    name: str
    status: str
    time: Optional[float] = None
    message: Optional[str] = None


@dataclass
class ExecutionEntity:
    """ Represents an execution run containing metadata and aggregated test results. """
    id: Optional[str]
    project: str
    environment: str
    source: str
    run_number: int
    created_at: datetime
    total: int
    failures: int
    skipped: int
    passed: Optional[int]
    pass_rate: float
    failure_rate: float
    skipped_rate: float
    tests: Optional[List[Dict[str, Any]]] = None
    failed_cases: Optional[List[Dict[str, Any]]] = None
    execution_date: Optional[datetime] = None
