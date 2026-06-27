"""This Python code defines a composer function to instantiate `GetFailedTestsUseCase`."""

from app.infrastructure.db.interfaces.database_adapter_interface import (
    DatabaseAdapterInterface
)
from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.application.use_cases.metrics.get_failed_tests_use_case import GetFailedTestsUseCase


def get_failed_tests_use_case_composer(db_wrapper: DatabaseAdapterInterface) -> GetFailedTestsUseCase:
    """This function composes and returns a GetFailedTestsUseCase instance."""

    repo = MetricsRepository(db_wrapper)
    use_case = GetFailedTestsUseCase(repo)
    return use_case
