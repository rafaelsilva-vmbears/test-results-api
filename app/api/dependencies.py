
from fastapi import Request, Depends
from app.infrastructure.db.adapters.mongo_adapter import MongoDatabaseAdapter
from app.application.use_cases.execution.create_exections_use_case import CreateExecutionUseCase
from app.application.use_cases.metrics.get_failed_tests_use_case import GetFailedTestsUseCase
from app.application.use_cases.metrics.get_run_summary_use_case import GetRunSummaryUseCase
from app.application.use_cases.execution.get_list_executions_use_case import (GetListExecutionsUseCase)
from app.application.use_cases.execution.get_execution_by_id_use_case import GetExecutionByIdUseCase
from app.application.use_cases.projects.get_projects_use_case import GetProjectsUseCase
from app.api.composer.create_execution_composer import create_execution_composer
from app.api.composer.list_executions_composer import list_execution_composer
from app.api.composer.get_projects_composer import get_projects_composer
from app.api.composer.get_failed_tests_use_case_compose import get_failed_tests_use_case_composer
from app.api.composer.get_run_summary_compose import get_run_summary_use_case_composer
from app.api.composer.get_execution_by_id_use_case_composer import get_execution_by_id_use_case_composer
from app.api.composer.get_module_health_use_case_composer import get_module_health_use_case_composer
from app.api.composer.get_flaky_tests_use_case_composer import get_flaky_tests_use_case_composer
from app.api.composer.get_stable_tests_use_case_composer import get_stable_tests_use_case_composer
from app.api.composer.get_trends_use_case_composer import get_trends_use_case_composer
from app.api.composer.get_test_cases_use_case_composer import get_test_cases_use_case_composer
from app.api.composer.get_mttr_use_case_composer import get_mttr_use_case_composer
from app.api.composer.get_performance_metrics_use_case_composer import get_performance_metrics_use_case_composer
from app.application.use_cases.metrics.get_module_health_use_case import GetModuleHealthUseCase
from app.application.use_cases.metrics.get_flaky_tests_use_case import GetFlakyTestsUseCase
from app.application.use_cases.metrics.get_stable_tests_use_case import GetStableTestsUseCase
from app.application.use_cases.metrics.get_trends_use_case import GetTrendsUseCase
from app.application.use_cases.metrics.get_test_cases_use_case import GetTestCasesUseCase
from app.application.use_cases.metrics.get_mttr_use_case import GetMTTRUseCase
from app.application.use_cases.metrics.get_common_errors_use_case import GetCommonErrorsUseCase
from app.api.composer.get_common_errors_use_case_composer import get_common_errors_use_case_composer
from app.application.use_cases.metrics.get_performance_metrics_use_case import GetPerformanceMetricsUseCase
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)

def get_db_adapter(request: Request) -> MongoDatabaseAdapter:
    return request.app.state.db_adapter

def get_create_execution_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> CreateExecutionUseCase:
    return create_execution_composer(adapter)

def get_list_executions_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetListExecutionsUseCase:
    return list_execution_composer(adapter)

def get_failed_tests_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetFailedTestsUseCase:
    return get_failed_tests_use_case_composer(adapter)

def get_run_summary_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetRunSummaryUseCase:
    return get_run_summary_use_case_composer(adapter)

def get_execution_by_id_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetExecutionByIdUseCase:
    return get_execution_by_id_use_case_composer(adapter)

def get_projects_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetProjectsUseCase:
    return get_projects_composer(adapter)

def get_module_health_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetModuleHealthUseCase:
    return get_module_health_use_case_composer(adapter)

def get_flaky_tests_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetFlakyTestsUseCase:
    return get_flaky_tests_use_case_composer(adapter)

def get_stable_tests_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetStableTestsUseCase:
    return get_stable_tests_use_case_composer(adapter)

def get_trends_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetTrendsUseCase:
    return get_trends_use_case_composer(adapter)

def get_test_cases_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetTestCasesUseCase:
    return get_test_cases_use_case_composer(adapter)

def get_mttr_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetMTTRUseCase:
    return get_mttr_use_case_composer(adapter)

def get_common_errors_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetCommonErrorsUseCase:
    return get_common_errors_use_case_composer(adapter)

def get_performance_metrics_use_case(adapter: MongoDatabaseAdapter = Depends(get_db_adapter),) -> GetPerformanceMetricsUseCase:
    return get_performance_metrics_use_case_composer(adapter)

