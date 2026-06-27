from datetime import datetime
from typing import List

from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.domain.entities.common_error_summary import CommonErrorSummary
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)

class GetCommonErrorsUseCase:
    """Use case to get common errors grouped by message."""

    def __init__(self, metrics_repository: MetricsRepositoryInterface):
        self.metrics_repository = metrics_repository

    def execute(
        self, project: str, environment: str, start_dt: datetime, end_dt: datetime
    ) -> List[CommonErrorSummary]:
        try:
            logger.info("Executing GetCommonErrorsUseCase for project: %s", project)
            return self.metrics_repository.get_common_errors(
                project, environment, start_dt, end_dt
            )
        except Exception as e:
            logger.error("Error in GetCommonErrorsUseCase: %s", e)
            raise e
