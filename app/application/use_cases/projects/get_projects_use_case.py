from typing import Any, Dict, List, Optional
from app.domain.interfaces.project_repository_interface import ProjectRepository

class GetProjectsUseCase:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def execute(self, name: Optional[str], limit: int) -> List[Dict[str, Any]]:
        return self.repository.list_projects(name=name, limit=limit)
