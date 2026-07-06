"""
This module defines the GetFailedTestsUseCase class,
which retrieves and processes data about failed tests for a given project.

Classes:
    GetFailedTestsUseCase: A use case for fetching and processing failed test metrics.

Dependencies:
    MetricsRepositoryInterface: An interface for accessing metrics data, injected as a dependency.
"""

from datetime import datetime
from typing import Optional, List
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.application.dtos.metrics_dto import FailedTestDTO
from app.infrastructure.logging.logging_config import get_logger


logger = get_logger(__name__)


class GetFailedTestsUseCase:
    """A use case for fetching and processing failed test metrics."""

    def __init__(self, repository: MetricsRepositoryInterface):
        self.repo = repository

    def execute(self, project: str, environment: str, start_dt: Optional[datetime] = None, end_dt: Optional[datetime] = None, last_runs: Optional[int] = None) -> List[FailedTestDTO]:
        """Retrieve and process failed test metrics for the specified project and date range."""

        project = project.strip().lower()
        environment = environment.strip().lower()

        if project is None or not project.strip():
            raise ValueError(
                "Project name must be provided and cannot be empty.")

        if environment is None or not environment.strip():
            raise ValueError(
                "Environment must be provided and cannot be empty.")

        if start_dt and end_dt and start_dt > end_dt:
            raise ValueError("Start date must be before end date.")

        data = self.repo.get_failed_tests(
            project, environment, start_dt, end_dt, last_runs)

        if not data:
            return []

        # Processa os dados para garantir que estão no formato correto
        processed_data = []
        for item in data:
            processed_item = FailedTestDTO(
                name=item.name,
                run_numbers=sorted(item.run_numbers),
                last_message=item.last_message
            )
            processed_data.append(processed_item)

        return processed_data
