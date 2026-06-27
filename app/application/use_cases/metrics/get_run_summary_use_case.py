"""Implements the use case to retrieve and process metrics summaries."""

from datetime import datetime
from typing import Optional
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.application.dtos.metrics_dto import MetricsSummaryDTO
from app.infrastructure.logging.logging_config import get_logger


logger = get_logger(__name__)


class GetRunSummaryUseCase:
    """Class responsible for retrieving and processing metrics summaries from a repository."""

    def __init__(self, repository: MetricsRepositoryInterface):
        self.repo = repository

    def execute(
        self,
        project: str,
        environment: str,
        start_dt: datetime,
        end_dt: datetime
    ) -> Optional[MetricsSummaryDTO]:
        """Retrieves and processes metrics summaries for the given project and environment."""

        project = project.strip().lower()
        environment = environment.strip().lower()

        if project is None or not project.strip():
            raise ValueError(
                "Project name must be provided and cannot be empty.")

        if environment is None or not environment.strip():
            raise ValueError(
                "Environment must be provided and cannot be empty.")

        if start_dt > end_dt:
            raise ValueError("Start date must be before end date.")

        summary = self.repo.get_summary(project, environment, start_dt, end_dt)

        if not summary:
            logger.info(
                "No metrics summary found for project: %s, environment: %s", project, environment)
            return None

        # Rounding logic for DTO
        avg_pass_rate = round(summary.avg_pass_rate, 2)
        avg_failures = round(summary.avg_failures, 2)
        avg_skipped = round(summary.avg_skipped, 2)

        entity = MetricsSummaryDTO(
            project=summary.project,
            environment=summary.environment,
            total_runs=summary.total_runs,
            total_tests=summary.total_tests,
            total_passes=summary.total_passes,
            total_failures=summary.total_failures,
            total_skipped=summary.total_skipped,
            avg_pass_rate=avg_pass_rate,
            avg_failures=avg_failures,
            avg_skipped=avg_skipped,
            last_run_number=summary.last_run_number,
            last_execution_date=summary.last_execution_date
        )

        logger.info("Metrics summary processed successfully with total_runs: %d, total_tests: %d",
                    summary.total_runs, summary.total_tests)

        return entity
