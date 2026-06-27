from app.application.use_cases.metrics.get_performance_metrics_use_case import GetPerformanceMetricsUseCase
from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface

def get_performance_metrics_use_case_composer(adapter: DatabaseAdapterInterface) -> GetPerformanceMetricsUseCase:
    repository = MetricsRepository(adapter)
    return GetPerformanceMetricsUseCase(repository)
