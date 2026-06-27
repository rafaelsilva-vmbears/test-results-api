from typing import List

from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


class GetTestCasesUseCase:
    """Use case to get a list of all distinct test cases."""

    def __init__(self, metrics_repository: MetricsRepositoryInterface):
        self.metrics_repository = metrics_repository

    def execute(self, project: str, environment: str) -> List[str]:
        try:
            logger.info("Executing GetTestCasesUseCase for project: %s", project)
            return self.metrics_repository.get_test_cases(project, environment)
        except Exception as e:
            logger.error("Error in GetTestCasesUseCase: %s", e)
            raise e
