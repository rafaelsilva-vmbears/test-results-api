"""
This module defines the MetricsRepositoryInterface protocol,
which outlines the methods for interacting with metrics data.
It includes methods for retrieving summaries and failed test details,
optionally filtered by date ranges.
"""

from datetime import datetime
from typing import Protocol, Optional, List
from app.domain.entities.metrics_summary import MetricsSummary
from app.domain.entities.failed_test_summary import FailedTestSummary


from app.domain.entities.module_health_summary import ModuleHealthSummary
from app.domain.entities.flaky_test_summary import FlakyTestSummary
from app.domain.entities.trend_summary import TrendSummary
from app.domain.entities.mttr_summary import MTTRSummary
from app.domain.entities.common_error_summary import CommonErrorSummary
from app.domain.entities.performance_metrics import PerformanceMetricsSummary

class MetricsRepositoryInterface(Protocol):
    """Defines the interface for interacting with metrics data."""

    def get_summary(
        self,
        project: str,
        environment: str,
        start_dt: datetime,
        end_dt: datetime
    ) -> Optional[MetricsSummary]:
        """Retrieve a summary of metrics for a given project,
        optionally filtered by a date range."""

    def get_failed_tests(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> List[FailedTestSummary]:
        """Retrieve a list of failed tests for a project,
                optionally filtered by a date range."""

    def get_module_health(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> List[ModuleHealthSummary]:
        """Retrieve a list of modules and their failure counts."""

    def get_flaky_tests(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> List[FlakyTestSummary]:
        """Retrieve a list of flaky tests with instability scores."""

    def get_trends(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> List[TrendSummary]:
        """Retrieve trends grouped by day."""

    def get_test_cases(
            self,
            project: str,
            environment: str) -> List[str]:
        """Retrieve a distinct list of all test cases for a project."""

    def get_mttr(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> MTTRSummary:
        """Calculate Mean Time To Recovery for broken tests."""

    def get_common_errors(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> List[CommonErrorSummary]:
        """Retrieve a list of common errors grouped by message."""

    def get_performance_metrics(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> 'PerformanceMetricsSummary':
        """Retrieve average execution time and slowest tests."""
