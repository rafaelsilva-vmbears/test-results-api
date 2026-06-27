from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

class ProjectRepository(ABC):
    @abstractmethod
    async def upsert_seen(self, project: str, seen_at: datetime) -> None:
        ...

    @abstractmethod
    async def list(self, q: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[dict]:
        ...
