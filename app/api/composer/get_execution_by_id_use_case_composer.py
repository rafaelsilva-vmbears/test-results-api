"""This file defines a composer function to instantiate `GetListExecutionsUseCase`."""

from app.infrastructure.db.interfaces.database_adapter_interface import (
    DatabaseAdapterInterface
)
from app.infrastructure.repositories.execution_repository import ExecutionRepository
from app.application.use_cases.execution.get_execution_by_id_use_case import (
    GetExecutionByIdUseCase
)


def get_execution_by_id_use_case_composer(
    database_adapter: DatabaseAdapterInterface
) -> GetExecutionByIdUseCase:
    """Composes and returns the GetExecutionByIdUseCase instance."""
    repository = ExecutionRepository(database_adapter)
    return GetExecutionByIdUseCase(repository)
