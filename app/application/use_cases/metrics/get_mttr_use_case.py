from datetime import datetime

from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.domain.entities.mttr_summary import MTTRSummary
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


class GetMTTRUseCase:
    """Use case to get MTTR."""

    def __init__(self, metrics_repository: MetricsRepositoryInterface):
        self.metrics_repository = metrics_repository

    def execute(self, project: str, environment: str, start_dt: datetime, end_dt: datetime) -> MTTRSummary:
        try:
            logger.info("Executing GetMTTRUseCase for project: %s", project)
            return self.metrics_repository.get_mttr(project, environment, start_dt, end_dt)
        except Exception as e:
            logger.error("Error in GetMTTRUseCase: %s", e)
            raise e
