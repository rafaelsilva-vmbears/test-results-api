""" FastAPI router for managing test executions. """

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Tuple

from fastapi import APIRouter, Query, Body, Depends, Path, HTTPException
from starlette import status

from app.api.schemas.execution import (
    ExecutionCreateSchema,
    ExecutionListItemSchema,
    ErrorResponseSchema,
    CreateExecutionResponseSchema,
)
from app.application.dtos.execution_dto import CreateExecutionDTO, TestDTO
from app.infrastructure.security.security import verify_read_permission, verify_write_permission
from app.infrastructure.logging.logging_config import get_logger
from app.application.use_cases.execution.create_exections_use_case import (
    CreateExecutionUseCase,
)
from app.application.use_cases.execution.get_list_executions_use_case import (
    GetListExecutionsUseCase,
)
from app.application.use_cases.execution.get_execution_by_id_use_case import (
    GetExecutionByIdUseCase,
)
from app.api.dependencies import (
    get_execution_by_id_use_case,
    get_create_execution_use_case,
    get_list_executions_use_case,
)
from app.utils.query_filters import get_metrics_filters, MetricsFilter


BR_ZONE_INFO = ZoneInfo("America/Sao_Paulo")
logger = get_logger(__name__)

router = APIRouter(
    prefix="/executions",
    tags=["Executions"],
    # Removed global dependency to apply specific ones on routes
)

# ==========================================================
#  POST /executions  → cria uma nova execução de testes
# ==========================================================


@router.post(
    "",
    summary="Register new test execution",
    status_code=200,
    response_model=CreateExecutionResponseSchema,
    responses={
        201: {
            "id": "string",
        },
        400: {
            "model": ErrorResponseSchema,
            "description": "Erro de validação nos dados da execução",
        },
    },
    dependencies=[Depends(verify_write_permission)],
)
def create_execution(
    payload: ExecutionCreateSchema = Body(...),
    project: str = Query(..., description="Nome do projeto (obrigatório)"),
    environment: str = Query(
        ...,
        description="Ambiente da execução (obrigatório)",
    ),
    source: str = Query(description="Fonte dos testes", default="xml"),
    use_case: CreateExecutionUseCase = Depends(get_create_execution_use_case),
):
    """
    Create a new test run for the specified project.
    """

    # Mantém logica de default do created_at se nao vier no payload
    created_at_val = (
        payload.created_at
        if payload.created_at
        else datetime.now(BR_ZONE_INFO).isoformat()
    )

    # Convert Pydantic Schema to Application DTO
    dto = CreateExecutionDTO(
        total=payload.total,
        passed=payload.passed,
        failures=payload.failures,
        errors=payload.errors,
        skipped=payload.skipped,
        pass_rate=payload.pass_rate,
        failure_rate=payload.failure_rate,
        skipped_rate=payload.skipped_rate,
        time=payload.time,
        source=source.lower(),  # Usa o source da query, conforme logica original
        tests=[TestDTO(**t.model_dump()) for t in payload.tests],
        failed_cases=[TestDTO(**t.model_dump()) for t in payload.failed_cases],
        created_at=created_at_val,
    )

    entity = use_case.execute(
        dto,
        project.lower(),
        environment.lower(),
    )
    return CreateExecutionResponseSchema(id=str(entity.id))


# ==========================================================
#  GET /executions → lista execuções filtradas
# ==========================================================


@router.get(
    "",
    summary="List test runs by project and period",
    response_model=List[ExecutionListItemSchema],
    responses={
        200: {
            "description": "Lista de execuções encontradas",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "string",
                            "project": "string",
                            "environment": "string",
                            "run_number": 0,
                            "created_at": "string",
                            "total": 0,
                            "failures": 0,
                            "skipped": 0,
                            "passed": 0,
                            "tests": [
                                {
                                    "name": "string",
                                    "status": "string",
                                    "time": 0,
                                    "message": "string",
                                }
                            ],
                            "failed_cases": [
                                {
                                    "name": "string",
                                    "status": "string",
                                    "time": 0,
                                    "message": None,
                                }
                            ],
                        }
                    ]
                }
            },
        },
    },
    dependencies=[Depends(verify_read_permission)],
)
def list_executions(
    project: str = Query(..., description="Nome do projeto (obrigatório)"),
    environment: str = Query(
        ...,
        description="Ambiente da execução (obrigatório)",
    ),
    filters: MetricsFilter = Depends(get_metrics_filters),
    limit: int = Query(
        50,
        ge=1,
        le=500,
        description="Número máximo de resultados (1-500). Ignorado se last_runs for usado.",
    ),
    use_case: GetListExecutionsUseCase = Depends(get_list_executions_use_case),
):
    """
    Lists test runs filtered by **project** and **period** or **last runs**.
    """
    executions_list = use_case.execute(
        project.lower(),
        environment.lower(),
        filters.start_dt,
        filters.end_dt,
        filters.last_runs if filters.last_runs else limit,
    )
    return executions_list


# ==========================================================
#  GET /executions/{id} → execução por id
# ==========================================================


@router.get(
    "/{execution_id}",
    summary="Get execution by ID",
    response_model=ExecutionListItemSchema,
    responses={
        200: {
            "description": "Detalhes da execução encontrados",
        },
    },
    dependencies=[Depends(verify_read_permission)],
)
def get_execution_by_id(
    execution_id: str = Path(..., description="ID da execução (obrigatório)"),
    use_case: GetExecutionByIdUseCase = Depends(get_execution_by_id_use_case),
):
    """Fetches a specific test execution by its ID."""
    execution = use_case.execute(execution_id)

    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with ID '{execution_id}' not found.",
        )

    return execution
