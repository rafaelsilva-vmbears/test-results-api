from datetime import datetime
from typing import Optional, Tuple
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.domain.entities.performance_metrics import PerformanceMetricsSummary

class GetPerformanceMetricsUseCase:
    def __init__(self, metrics_repository: MetricsRepositoryInterface):
        self.metrics_repository = metrics_repository

    def execute(
        self,
        project: str,
        environment: str,
        start_dt: Optional[datetime] = None, end_dt: Optional[datetime] = None, last_runs: Optional[int] = None
    ) -> PerformanceMetricsSummary:
        return self.metrics_repository.get_performance_metrics(
            project, environment, start_dt, end_dt, last_runs
        )
