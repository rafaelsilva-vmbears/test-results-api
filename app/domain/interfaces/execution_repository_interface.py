# app/domain/interfaces/execution_repository_interface.py

"""
    Repository Interface
"""
from typing import Protocol, List, Optional
from datetime import datetime
from app.domain.entities.execution_entity import ExecutionEntity


class ExecutionRepositoryInterface(Protocol):
    """Repository Interface for execution data access."""

    #def get_next_run_number(self, project: str) -> int:
    #    """Retorna próximo run_number para o projeto."""

    def get_next_run_number(self, project: str, environment: str) -> int:
        """Retorna próximo run_number para o projeto."""

    def insert_execution(self, execution: ExecutionEntity) -> str:
        """Insere e retorna o id como string."""

    def find_executions(
        self,
        project: str,
        environment: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[ExecutionEntity]:
        """Finds executions based on filters."""

    def get_execution_by_id(
        self,
        execution_id: str,
    ) -> ExecutionEntity | None:
        """Retrieves an execution entity by its ID."""
