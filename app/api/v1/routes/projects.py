from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.infrastructure.security.security import verify_api_key
from app.api.dependencies import get_projects_use_case
from app.application.use_cases.projects.get_projects_use_case import GetProjectsUseCase
from app.api.schemas.projects import ProjectListItem

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    dependencies=[Depends(verify_api_key)],
)

@router.get(
    "",
    response_model=List[ProjectListItem],
    summary="List projects",
    responses={
        200: {
            "description": "Lista de projetos encontrados",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "string",
                            "name": "string",
                            "created_at": "string",
                            "last_seen_at": "string",
                            "total_runs": 0,
                            "environments": ["string", "string"],
                        }
                    ]
                }
            },
        }
    },
)
def list_projects(
    name: str = Query(default=None, description="Project name (Example: 'homepoint legado')"),
    limit: int = Query(default=50, ge=1, le=200),
    use_case: GetProjectsUseCase = Depends(get_projects_use_case),
):
    docs = use_case.execute(name=name, limit=limit)

    result: List[ProjectListItem] = []
    for d in docs:
        project_id = d.get("id")  # vem do adapter (_id -> id)
        project_name = d.get("name") or project_id

        result.append(
            ProjectListItem(
                id=project_id,
                name=project_name,
                created_at=d.get("created_at"),
                last_seen_at=d.get("last_seen_at"),
                environments=d.get("environments", []),
            )
        )

    return result
