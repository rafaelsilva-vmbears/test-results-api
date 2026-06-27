from app.application.use_cases.metrics.get_mttr_use_case import GetMTTRUseCase
from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface

def get_mttr_use_case_composer(adapter: DatabaseAdapterInterface) -> GetMTTRUseCase:
    repository = MetricsRepository(adapter)
    return GetMTTRUseCase(repository)
