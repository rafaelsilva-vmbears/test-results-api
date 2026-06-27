from datetime import datetime
from typing import Tuple
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.domain.entities.performance_metrics import PerformanceMetricsSummary

class GetPerformanceMetricsUseCase:
    def __init__(self, metrics_repository: MetricsRepositoryInterface):
        self.metrics_repository = metrics_repository

    def execute(
        self,
        project: str,
        environment: str,
        start_dt: datetime,
        end_dt: datetime
    ) -> PerformanceMetricsSummary:
        return self.metrics_repository.get_performance_metrics(
            project, environment, start_dt, end_dt
        )
