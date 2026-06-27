from app.application.use_cases.metrics.get_common_errors_use_case import GetCommonErrorsUseCase
from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface

def get_common_errors_use_case_composer(adapter: DatabaseAdapterInterface) -> GetCommonErrorsUseCase:
    """Composer for GetCommonErrorsUseCase."""
    repository = MetricsRepository(adapter)
    return GetCommonErrorsUseCase(repository)
