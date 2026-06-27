"""This file defines a composer function to instantiate `GetListExecutionsUseCase`."""

from app.infrastructure.db.interfaces.database_adapter_interface import (
    DatabaseAdapterInterface
)
from app.infrastructure.repositories.execution_repository import ExecutionRepository
from app.application.use_cases.execution.get_list_executions_use_case import (
    GetListExecutionsUseCase
)


def list_execution_composer(db_wrapper: DatabaseAdapterInterface) -> GetListExecutionsUseCase:
    """This function composes and returns a GetListExecutionsUseCase
    instance by setting up the necessary dependencies."""

    repo = ExecutionRepository(db_wrapper)
    use_case = GetListExecutionsUseCase(repo)
    return use_case
