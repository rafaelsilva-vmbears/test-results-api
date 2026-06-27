from app.application.use_cases.metrics.get_test_cases_use_case import GetTestCasesUseCase
from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface

def get_test_cases_use_case_composer(adapter: DatabaseAdapterInterface) -> GetTestCasesUseCase:
    repository = MetricsRepository(adapter)
    return GetTestCasesUseCase(repository)
