from datetime import datetime
from typing import List

from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.domain.entities.trend_summary import TrendSummary
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


class GetTrendsUseCase:
    """Use case to get test trends over time."""

    def __init__(self, metrics_repository: MetricsRepositoryInterface):
        self.metrics_repository = metrics_repository

    def execute(self, project: str, environment: str, start_dt: datetime, end_dt: datetime) -> List[TrendSummary]:
        try:
            logger.info("Executing GetTrendsUseCase for project: %s", project)
            return self.metrics_repository.get_trends(project, environment, start_dt, end_dt)
        except Exception as e:
            logger.error("Error in GetTrendsUseCase: %s", e)
            raise e
