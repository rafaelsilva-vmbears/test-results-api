

"""This module defines the GetExecutionByIdUseCase class,
which handles the retrieval of execution details by ID."""

from app.infrastructure.logging.logging_config import get_logger
from app.domain.interfaces.execution_repository_interface import ExecutionRepositoryInterface
from app.domain.entities.execution_entity import ExecutionEntity
logger = get_logger(__name__)


class GetExecutionByIdUseCase:
    """This class provides a use case for retrieving execution details by ID."""

    def __init__(self, repository: ExecutionRepositoryInterface):
        self.repository = repository

    def execute(self, execution_id: str) -> ExecutionEntity | None:
        """
        Executes the use case to retrieve execution details by ID.
        Returns the Execution entity if found, otherwise None.
        """

        execution = self.repository.get_execution_by_id(execution_id)

        if execution is None:
            logger.info(
                'Execution not found in repository for ID: %s', execution_id
            )
        return execution
