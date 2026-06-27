from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class ApiKey:
    key: str
    team_name: str
    permissions: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    id: str = field(default="")

    def revoke(self):
        self.is_active = False
