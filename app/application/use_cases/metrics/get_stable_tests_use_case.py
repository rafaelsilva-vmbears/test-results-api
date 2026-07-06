"""Implements the use case to retrieve stable tests."""

from datetime import datetime
from typing import List, Optional
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.domain.entities.stable_test_summary import StableTestSummary


class GetStableTestsUseCase:
    """Class responsible for retrieving stable tests from a repository."""

    def __init__(self, repository: MetricsRepositoryInterface):
        self.repo = repository

    def execute(
        self,
        project: str,
        environment: str,
        start_dt: Optional[datetime] = None, end_dt: Optional[datetime] = None, last_runs: Optional[int] = None
    ) -> List[StableTestSummary]:
        """Retrieves tests that are consistently passing with high reliability."""
        
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

        return self.repo.get_stable_tests(project, environment, start_dt, end_dt, last_runs)
