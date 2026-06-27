from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface
from app.infrastructure.repositories.projects_repository import ProjectsRepository
from app.application.use_cases.projects.get_projects_use_case import GetProjectsUseCase

def get_projects_composer(adapter: DatabaseAdapterInterface) -> GetProjectsUseCase:
    repo = ProjectsRepository(adapter)
    return GetProjectsUseCase(repo)
