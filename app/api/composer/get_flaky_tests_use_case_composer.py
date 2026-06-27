from app.application.use_cases.metrics.get_flaky_tests_use_case import GetFlakyTestsUseCase
from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.infrastructure.db.adapters.mongo_adapter import MongoDatabaseAdapter

def get_flaky_tests_use_case_composer(adapter: MongoDatabaseAdapter) -> GetFlakyTestsUseCase:
    """Compose the GetFlakyTestsUseCase with its dependencies."""
    repository = MetricsRepository(adapter)
    return GetFlakyTestsUseCase(repository)
