from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class TestDTO:
    name: str
    status: str
    time: Optional[float] = None
    message: Optional[str] = None
    classname: Optional[str] = None
    run_number: int = 0
    short_name: Optional[str] = None

@dataclass
class CreateExecutionDTO:
    total: int
    failures: int
    skipped: int
    pass_rate: float
    failure_rate: float
    skipped_rate: float
    source: str
    tests: List[TestDTO]
    failed_cases: List[TestDTO]
    created_at: datetime
    execution_date: Optional[datetime] = None
    passed: Optional[int] = None
    errors: Optional[int] = None
    time: Optional[float] = None
