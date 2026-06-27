from datetime import datetime
from typing import TypedDict, List, Optional, Any

class ExecutionDocument(TypedDict, total=False):
    """
    Type definition for the Execution document as stored in MongoDB.
    total=False allows for optional fields like '_id'.
    """
    _id: Any  # ObjectId
    project: str
    environment: str
    run_number: int
    created_at: datetime
    execution_date: Optional[datetime]
    source: Optional[str]
    total: int
    failures: int
    skipped: int
    passed: int
    pass_rate: float
    failure_rate: float
    skipped_rate: float
    test_results: List[Any]  # Could be refined further if needed
    failed_cases: List[Any]  # Could be refined further if needed
