from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.domain.entities.permission_enum import Permission

class ApiKeyCreateRequest(BaseModel):
    team_name: str
    permissions: List[Permission] = []

class ApiKeyUpdateRequest(BaseModel):
    permissions: List[Permission]

class ApiKeyResponse(BaseModel):
    id: str
    key: str
    team_name: str
    permissions: List[str]
    created_at: datetime
    is_active: bool
