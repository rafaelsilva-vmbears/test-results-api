import pytest
from unittest.mock import create_autospec
from datetime import datetime

from app.application.use_cases.metrics.get_module_health_use_case import GetModuleHealthUseCase
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.domain.entities.module_health_summary import ModuleHealthSummary

@pytest.fixture
def mock_repo():
    return create_autospec(MetricsRepositoryInterface, instance=True)

@pytest.fixture
def sut(mock_repo):
    return GetModuleHealthUseCase(repository=mock_repo)

class TestGetModuleHealthUseCase:

    def test_should_return_module_health_when_data_exists(self, sut, mock_repo):
        project_name = "RedeAgro"
        env_name = "production"
        start_dt = datetime(2023, 1, 1)
        end_dt = datetime(2023, 1, 31)

        domain_entity = [
            ModuleHealthSummary(module_name="ModuleA", fail_count=10)
        ]
        mock_repo.get_module_health.return_value = domain_entity

        result = sut.execute(project_name, env_name, start_dt, end_dt)

        mock_repo.get_module_health.assert_called_once_with(
            "redeagro", "production", start_dt, end_dt
        )
        assert result == domain_entity

    def test_should_raise_validation_error_when_project_is_empty(self, sut):
        with pytest.raises(ValueError, match="Project name must be provided and cannot be empty."):
            sut.execute("", "dev", datetime.now(), datetime.now())

    def test_should_raise_validation_error_when_environment_is_empty(self, sut):
        with pytest.raises(ValueError, match="Environment must be provided and cannot be empty."):
            sut.execute("proj", "", datetime.now(), datetime.now())

    def test_should_raise_validation_error_when_dates_are_inverted(self, sut):
        start = datetime(2023, 2, 1)
        end = datetime(2023, 1, 1)
        with pytest.raises(ValueError, match="Start date must be before end date."):
            sut.execute("proj", "env", start, end)

    def test_should_normalize_input_strings(self, sut, mock_repo):
        mock_repo.get_module_health.return_value = []
        sut.execute("  MyProject  ", "  PROD  ", datetime.now(), datetime.now())

        call_args = mock_repo.get_module_health.call_args
        assert call_args.args[0] == "myproject"
        assert call_args.args[1] == "prod"
