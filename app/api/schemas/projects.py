from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ProjectEnvironment(BaseModel):
    name: str
    total_runs: int


class ProjectListItem(BaseModel):
    id: Optional[str] = None

    name: str
    created_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None

    environments: List[ProjectEnvironment] = Field(default_factory=list)
