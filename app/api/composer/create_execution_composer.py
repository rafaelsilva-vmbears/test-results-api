"""This file defines a composer function to instantiate the `CreateExecutionUseCase`."""
from app.infrastructure.db.interfaces.database_adapter_interface import (
    DatabaseAdapterInterface
)
from app.infrastructure.repositories.execution_repository import ExecutionRepository
from app.application.use_cases.execution.create_exections_use_case import CreateExecutionUseCase


def create_execution_composer(db_wrapper: DatabaseAdapterInterface) -> CreateExecutionUseCase:
    """This function sets up and returns a CreateExecutionUseCase instance."""

    repo = ExecutionRepository(db_wrapper)
    use_case = CreateExecutionUseCase(repo)
    return use_case
