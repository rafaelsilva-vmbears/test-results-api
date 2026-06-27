from app.application.use_cases.metrics.get_trends_use_case import GetTrendsUseCase
from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface

def get_trends_use_case_composer(adapter: DatabaseAdapterInterface) -> GetTrendsUseCase:
    repository = MetricsRepository(adapter)
    return GetTrendsUseCase(repository)
