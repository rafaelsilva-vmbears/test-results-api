from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class MTTRSummary:
    project: str
    environment: str
    mttr_hours: float
    total_recoveries: int
