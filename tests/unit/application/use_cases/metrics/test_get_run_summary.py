
import pytest
from unittest.mock import Mock, create_autospec
from datetime import datetime

from app.application.use_cases.metrics.get_run_summary_use_case import GetRunSummaryUseCase
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.domain.entities.metrics_summary import MetricsSummary
from app.application.dtos.metrics_dto import MetricsSummaryDTO

@pytest.fixture
def mock_repo():
    return create_autospec(MetricsRepositoryInterface, instance=True)

@pytest.fixture
def sut(mock_repo):
    return GetRunSummaryUseCase(repository=mock_repo)

class TestGetRunSummaryUseCase:

    def test_should_return_rounded_summary_when_data_exists(self, sut, mock_repo):
        """
        GIVEN a project and environment with existing metrics
        WHEN execute is called
        THEN it should return a DTO with values rounded to 2 decimal places
        """
        project_name = "RedeAgro"
        env_name = "production"
        start_dt = datetime(2023, 1, 1)
        end_dt = datetime(2023, 1, 31)

        domain_entity = MetricsSummary(
            project=project_name,
            environment=env_name,
            total_runs=10,
            total_tests=1000,
            total_passes=950,
            total_failures=50,
            total_skipped=0,
            avg_pass_rate=95.123456,
            avg_failures=4.876544,
            avg_skipped=0.0,
            last_run_number=10,
            last_execution_date=datetime(2023, 1, 31)
        )
        mock_repo.get_summary.return_value = domain_entity

        result = sut.execute(project_name, env_name, start_dt, end_dt)

        mock_repo.get_summary.assert_called_once_with(
            "redeagro", "production", start_dt, end_dt
        )
        assert isinstance(result, MetricsSummaryDTO)
        assert result.avg_pass_rate == 95.12
        assert result.avg_failures == 4.88

    def test_should_return_none_when_repository_returns_empty(self, sut, mock_repo):
        mock_repo.get_summary.return_value = None
        result = sut.execute("proj", "env", datetime.now(), datetime.now())
        assert result is None

    def test_should_raise_validation_error_when_project_is_empty(self, sut):
        with pytest.raises(ValueError, match="Project name must be provided"):
            sut.execute("", "dev", datetime.now(), datetime.now())

    def test_should_raise_validation_error_when_dates_are_inverted(self, sut):
        start = datetime(2023, 2, 1)
        end = datetime(2023, 1, 1)
        with pytest.raises(ValueError, match="Start date must be before end date"):
            sut.execute("proj", "env", start, end)

    def test_should_normalize_input_strings(self, sut, mock_repo):
        mock_repo.get_summary.return_value = None
        sut.execute("  MyProject  ", "  PROD  ", datetime.now(), datetime.now())

        call_args = mock_repo.get_summary.call_args
        assert call_args.args[0] == "myproject"
        assert call_args.args[1] == "prod"
