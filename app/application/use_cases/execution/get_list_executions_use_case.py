"""
This file defines the `GetListExecutionsUseCase` class,
responsible for retrieving a list of executions from a repository.

**Class:** `GetListExecutionsUseCase`
- **Dependencies:** `ExecutionRepositoryInterface` (for data access).
- **`__init__`**:  Initializes the use case with an `ExecutionRepositoryInterface` instance.
- **`execute`**:
    - Takes optional filters: `project` (string), `start_dt` (datetime),
    `end_dt` (datetime), and `limit` (integer, defaults to 50).'
"""

from typing import Optional
from datetime import datetime
from app.domain.interfaces.execution_repository_interface import ExecutionRepositoryInterface
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


class GetListExecutionsUseCase:
    """
    This class is responsible for retrieving a list of executions from a repository.
    """

    def __init__(self, repository: ExecutionRepositoryInterface):
        self.repo = repository

    def execute(
            self,
            project: str,
            environment: str,
            start_dt: Optional[datetime] = None,
            end_dt: Optional[datetime] = None,
            limit: int = 50):
        """ Executes the list with the provided parameters. """

        if start_dt and end_dt and start_dt > end_dt:
            raise ValueError("Start date must be before end date.")

        executions = self.repo.find_executions(
            project.lower(), environment.lower(), start_dt, end_dt, limit)

        return executions
