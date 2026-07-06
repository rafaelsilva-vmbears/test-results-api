"""
This module defines the API routes for project metrics,
including endpoints for retrieving summary metrics and failed tests within a specified date range.
It uses FastAPI dependencies for authentication, date validation, and use case implementations.
"""

from dataclasses import asdict
from datetime import datetime
from typing import List, Tuple
from fastapi import APIRouter, Query, Depends
from app.api.schemas.metrics import (
    ErrorResponseSchema, FailureItemSchema, MetricsSummaryResponseSchema,
    ModuleHealthItemSchema, FlakyTestItemSchema, TrendItemSchema, MTTRSummarySchema,
    CommonErrorItemSchema, PerformanceMetricsSchema
)

from app.infrastructure.security.security import verify_api_key
from app.application.use_cases.metrics.get_run_summary_use_case import GetRunSummaryUseCase
from app.application.use_cases.metrics.get_failed_tests_use_case import GetFailedTestsUseCase
from app.application.use_cases.metrics.get_module_health_use_case import GetModuleHealthUseCase
from app.application.use_cases.metrics.get_flaky_tests_use_case import GetFlakyTestsUseCase
from app.application.use_cases.metrics.get_trends_use_case import GetTrendsUseCase
from app.application.use_cases.metrics.get_test_cases_use_case import GetTestCasesUseCase
from app.application.use_cases.metrics.get_mttr_use_case import GetMTTRUseCase
from app.application.use_cases.metrics.get_common_errors_use_case import GetCommonErrorsUseCase
from app.application.use_cases.metrics.get_performance_metrics_use_case import GetPerformanceMetricsUseCase
from app.api.dependencies import (
    get_failed_tests_use_case, get_run_summary_use_case,
    get_module_health_use_case, get_flaky_tests_use_case,
    get_trends_use_case, get_test_cases_use_case, get_mttr_use_case,
    get_common_errors_use_case, get_performance_metrics_use_case
)
from app.utils.query_filters import get_metrics_filters, MetricsFilter

router = APIRouter(prefix="/metrics",
                   tags=["Metrics"], dependencies=[Depends(verify_api_key)])


# ==========================================================
#  GET /metrics/summary → resumo de métricas do projeto
# ==========================================================
@router.get(
    "/summary",
    summary="Get a summary of project metrics",
    response_model=MetricsSummaryResponseSchema | None,
    responses={
        200: {
            "description": "Resumo das execuções do projeto",
            "content": {
                "application/json": {
                    "example": {
                        "project": "string",
                        "total_runs": 0,
                        "total_tests": 0,
                        "avg_pass_rate": 0,
                        "avg_failures": 0,
                        "last_run_number": 0,
                        "last_execution_date": "string"
                    }
                }
            },
        },
        400: {"model": ErrorResponseSchema, "description": "Erro de validação nos parâmetros"},
    },
)
def get_metrics_summary(
    project: str = Query(..., description="Nome do projeto (obrigatório)"),
    environment: str = Query(...,
                             description="Ambiente do projeto (obrigatório)"),
    filters: MetricsFilter = Depends(get_metrics_filters),
    use_case: GetRunSummaryUseCase = Depends(get_run_summary_use_case)
):
    """
    Returns aggregated statistics of project executions:
    - Total executions (`total_runs`)
    - Total tests performed (`total_tests`)
    - Average success rate (`avg_pass_rate`)
    - Average failures per execution (`avg_failures`)
    - Last run number (`last_run_number`)
    - Date of last run (`last_execution_date`)
    """
    result = use_case.execute(
        project.lower(), environment.lower(), filters.start_dt, filters.end_dt, filters.last_runs)

    if result is None:
        return None

    return MetricsSummaryResponseSchema(**asdict(result))

# ==========================================================
#  GET /metrics/failures → lista de testes que falharam
# ==========================================================


@router.get(
    "/failures",
    summary="List failed tests and their executions",
    response_model=List[FailureItemSchema],
    responses={
        200: {
            "description": "Lista de testes com falhas agrupadas por nome",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "name": "string",
                            "run_numbers": [],
                            "last_message": "string"
                        }
                    ]
                }
            },
        },
        400: {"model": ErrorResponseSchema, "description": "Erro de validação nos parâmetros"},
    },
)
def get_failed_tests(
    project: str = Query(..., description="Nome do projeto (obrigatório)"),
    environment: str = Query(...,
                             description="Ambiente do projeto (obrigatório)"),
    filters: MetricsFilter = Depends(get_metrics_filters),
    use_case: GetFailedTestsUseCase = Depends(get_failed_tests_use_case)
):
    """
    Lists all tests that **failed** within the selected period.
    Returns the test name, execution number, and the last error message.
    """
    result = use_case.execute(
        project.lower(), environment.lower(), filters.start_dt, filters.end_dt, filters.last_runs)

    if not result:
        return []

    return [FailureItemSchema(**asdict(item)) for item in result]

# ==========================================================
#  GET /metrics/module-health → saúde dos módulos
# ==========================================================

@router.get(
    "/module-health",
    summary="Get health metrics grouped by module",
    response_model=List[ModuleHealthItemSchema],
    responses={
        200: {"description": "Lista de módulos e quantidade de falhas"},
        400: {"model": ErrorResponseSchema, "description": "Erro de validação"},
    },
)
def get_module_health(
    project: str = Query(..., description="Nome do projeto (obrigatório)"),
    environment: str = Query(..., description="Ambiente do projeto (obrigatório)"),
    filters: MetricsFilter = Depends(get_metrics_filters),
    use_case: GetModuleHealthUseCase = Depends(get_module_health_use_case)
):
    """
    Groups failed tests by their base module/package name
    and returns a count of failures per module.
    """
    result = use_case.execute(
        project.lower(), environment.lower(), filters.start_dt, filters.end_dt, filters.last_runs)

    if not result:
        return []

    return [ModuleHealthItemSchema(**asdict(item)) for item in result]

# ==========================================================
#  GET /metrics/flaky-tests → testes instáveis
# ==========================================================

@router.get(
    "/flaky-tests",
    summary="List flaky tests and their instability score",
    response_model=List[FlakyTestItemSchema],
    responses={
        200: {"description": "Lista de testes instáveis ordenados por instabilidade"},
        400: {"model": ErrorResponseSchema, "description": "Erro de validação"},
    },
)
def get_flaky_tests(
    project: str = Query(..., description="Nome do projeto (obrigatório)"),
    environment: str = Query(..., description="Ambiente do projeto (obrigatório)"),
    filters: MetricsFilter = Depends(get_metrics_filters),
    use_case: GetFlakyTestsUseCase = Depends(get_flaky_tests_use_case)
):
    """
    Identifies tests that fail intermittently across multiple runs.
    Returns the test name, number of failures, and instability score.
    """
    result = use_case.execute(
        project.lower(), environment.lower(), filters.start_dt, filters.end_dt, filters.last_runs)

    if not result:
        return []

    return [FlakyTestItemSchema(**asdict(item)) for item in result]

# ==========================================================
#  GET /metrics/trends → evolução de pass rate e falhas
# ==========================================================

@router.get(
    "/trends",
    summary="Get test execution trends over time",
    response_model=List[TrendItemSchema],
    responses={
        200: {"description": "Lista de tendências agrupadas por data"},
        400: {"model": ErrorResponseSchema, "description": "Erro de validação"},
    },
)
def get_trends(
    project: str = Query(..., description="Nome do projeto (obrigatório)"),
    environment: str = Query(..., description="Ambiente do projeto (obrigatório)"),
    filters: MetricsFilter = Depends(get_metrics_filters),
    use_case: GetTrendsUseCase = Depends(get_trends_use_case)
):
    """
    Returns aggregated metrics grouped by day.
    Useful for visualizing stability evolution over time.
    """
    result = use_case.execute(
        project.lower(), environment.lower(), filters.start_dt, filters.end_dt, filters.last_runs)

    if not result:
        return []

    return [TrendItemSchema(**asdict(item)) for item in result]

# ==========================================================
#  GET /metrics/test-cases → Catálogo de Testes (Task 3)
# ==========================================================

@router.get(
    "/test-cases",
    summary="Get a distinct catalog of all test cases",
    response_model=List[str],
    responses={
        200: {"description": "Lista de nomes de testes únicos"},
        400: {"model": ErrorResponseSchema, "description": "Erro de validação"},
    },
)
def get_test_cases(
    project: str = Query(..., description="Nome do projeto (obrigatório)"),
    environment: str = Query(..., description="Ambiente do projeto (obrigatório)"),
    use_case: GetTestCasesUseCase = Depends(get_test_cases_use_case)
):
    """
    Returns a distinct catalog of all test names ever executed
    for the specified project and environment.
    """
    result = use_case.execute(project.lower(), environment.lower())

    if not result:
        return []

    return result

# ==========================================================
#  GET /metrics/mttr → Mean Time To Recovery (Task 2)
# ==========================================================

@router.get(
    "/mttr",
    summary="Get Mean Time To Recovery (MTTR)",
    response_model=MTTRSummarySchema,
    responses={
        200: {"description": "Métricas de MTTR calculadas em horas"},
        400: {"model": ErrorResponseSchema, "description": "Erro de validação"},
    },
)
def get_mttr(
    project: str = Query(..., description="Nome do projeto (obrigatório)"),
    environment: str = Query(..., description="Ambiente do projeto (obrigatório)"),
    filters: MetricsFilter = Depends(get_metrics_filters),
    use_case: GetMTTRUseCase = Depends(get_mttr_use_case)
):
    """
    Returns the average time (in hours) it takes for a failed test
    to recover (pass) within the specified period.
    """
    result = use_case.execute(
        project.lower(), environment.lower(), filters.start_dt, filters.end_dt, filters.last_runs)

    if not result:
        return MTTRSummarySchema(project=project, environment=environment, mttr_hours=0.0, total_recoveries=0)

    return MTTRSummarySchema(**asdict(result))

# ==========================================================
#  GET /metrics/common-errors -> Common errors by message
# ==========================================================

@router.get(
    "/common-errors",
    summary="Get common test errors grouped by message",
    response_model=List[CommonErrorItemSchema],
    responses={
        200: {"description": "List of common error messages with frequency and affected tests/runs"},
        400: {"model": ErrorResponseSchema, "description": "Validation error"},
    },
)
def get_common_errors(
    project: str = Query(..., description="Project name (required)"),
    environment: str = Query(..., description="Environment (required)"),
    filters: MetricsFilter = Depends(get_metrics_filters),
    use_case: GetCommonErrorsUseCase = Depends(get_common_errors_use_case)
):
    """
    Returns aggregated test failures grouped by their error message.
    """
    result = use_case.execute(
        project.lower(), environment.lower(), filters.start_dt, filters.end_dt, filters.last_runs)

    if not result:
        return []

    return [CommonErrorItemSchema(**asdict(item)) for item in result]

@router.get(
    "/performance",
    summary="Get test suite performance metrics",
    response_model=PerformanceMetricsSchema,
    responses={
        200: {"description": "Performance metrics including avg execution time and slowest tests"},
        400: {"model": ErrorResponseSchema, "description": "Validation error"},
    },
)
def get_performance_metrics(
    project: str = Query(..., description="Project name (required)"),
    environment: str = Query(..., description="Environment (required)"),
    filters: MetricsFilter = Depends(get_metrics_filters),
    use_case: GetPerformanceMetricsUseCase = Depends(get_performance_metrics_use_case)
):
    """
    Returns performance metrics such as average execution duration and top 10 slowest tests.
    """
    result = use_case.execute(
        project.lower(), environment.lower(), filters.start_dt, filters.end_dt, filters.last_runs)

    return PerformanceMetricsSchema(**asdict(result))
