from app.application.use_cases.metrics.get_stable_tests_use_case import GetStableTestsUseCase
from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.infrastructure.db.adapters.mongo_adapter import MongoDatabaseAdapter

def get_stable_tests_use_case_composer(adapter: MongoDatabaseAdapter) -> GetStableTestsUseCase:
    """Compose the GetStableTestsUseCase with its dependencies."""
    repository = MetricsRepository(adapter)
    return GetStableTestsUseCase(repository)
