from datetime import datetime
from typing import Optional, List
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.domain.entities.flaky_test_summary import FlakyTestSummary
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)

class GetFlakyTestsUseCase:
    """A use case for fetching and processing flaky test metrics."""

    def __init__(self, repository: MetricsRepositoryInterface):
        self.repo = repository

    def execute(self, project: str, environment: str, start_dt: Optional[datetime] = None, end_dt: Optional[datetime] = None, last_runs: Optional[int] = None) -> List[FlakyTestSummary]:
        project = project.strip().lower()
        environment = environment.strip().lower()

        if not project:
            raise ValueError("Project name must be provided and cannot be empty.")

        if not environment:
            raise ValueError("Environment must be provided and cannot be empty.")

        if start_dt and end_dt and start_dt > end_dt:
            raise ValueError("Start date must be before end date.")

        return self.repo.get_flaky_tests(project, environment, start_dt, end_dt, last_runs)
