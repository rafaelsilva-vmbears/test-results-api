"""This Python module defines a composer function to instantiate `GetRunSummaryUseCase`."""

from app.infrastructure.db.interfaces.database_adapter_interface import (
    DatabaseAdapterInterface
)
from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.application.use_cases.metrics.get_run_summary_use_case import GetRunSummaryUseCase


def get_run_summary_use_case_composer(db_wrapper: DatabaseAdapterInterface) -> GetRunSummaryUseCase:
    """This function composes and returns a GetRunSummaryUseCase instance."""

    repo = MetricsRepository(db_wrapper)
    use_case = GetRunSummaryUseCase(repo)
    return use_case
