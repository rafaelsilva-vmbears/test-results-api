from app.application.use_cases.metrics.get_module_health_use_case import GetModuleHealthUseCase
from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.infrastructure.db.adapters.mongo_adapter import MongoDatabaseAdapter

def get_module_health_use_case_composer(adapter: MongoDatabaseAdapter) -> GetModuleHealthUseCase:
    """Compose the GetModuleHealthUseCase with its dependencies."""
    repository = MetricsRepository(adapter)
    return GetModuleHealthUseCase(repository)
