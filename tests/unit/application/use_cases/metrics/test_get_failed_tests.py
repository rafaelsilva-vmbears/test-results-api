
import pytest
from unittest.mock import Mock, create_autospec
from datetime import datetime

from app.application.use_cases.metrics.get_failed_tests_use_case import GetFailedTestsUseCase
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.application.dtos.metrics_dto import FailedTestDTO

@pytest.fixture
def mock_repo():
    return create_autospec(MetricsRepositoryInterface, instance=True)

@pytest.fixture
def sut(mock_repo):
    """Subject Under Test"""
    return GetFailedTestsUseCase(repository=mock_repo)

class TestGetFailedTestsUseCase:

    def test_should_return_dto_list_when_data_exists(self, sut, mock_repo):
        """
        GIVEN existing failures in repo
        WHEN execute is called
        THEN return list of FailedTestDTO
        """
        # Arrange
        start = datetime(2023, 1, 1)
        end = datetime(2023, 1, 31)

        # Mocking return from repo (duck typing or use a dataclass if available)
        mock_item = Mock()
        mock_item.name = "test.failed.Case"
        mock_item.run_numbers = [1, 5, 10]
        mock_item.last_message = "Timeout"

        mock_repo.get_failed_tests.return_value = [mock_item]

        # Act
        result = sut.execute("Prob", "Env", start, end)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], FailedTestDTO)
        assert result[0].name == "test.failed.Case"
        assert result[0].run_numbers == [1, 5, 10]

    def test_should_sort_run_numbers(self, sut, mock_repo):
        """
        GIVEN unsorted run numbers from repo
        WHEN execute is called
        THEN DTO should have sorted numbers
        """
        mock_item = Mock()
        mock_item.name = "test"
        mock_item.run_numbers = [10, 1, 5]
        mock_item.last_message = "msg"
        mock_repo.get_failed_tests.return_value = [mock_item]

        result = sut.execute("p", "e", datetime.now(), datetime.now())

        assert result[0].run_numbers == [1, 5, 10]

    def test_should_return_empty_list_when_no_data(self, sut, mock_repo):
        mock_repo.get_failed_tests.return_value = []
        result = sut.execute("p", "e", datetime.now(), datetime.now())
        assert result == []

    def test_validations(self, sut):
        # Empty project
        with pytest.raises(ValueError):
            sut.execute("", "e", datetime.now(), datetime.now())

        # Invalid date
        with pytest.raises(ValueError):
            sut.execute("p", "e", datetime(2023, 2, 1), datetime(2023, 1, 1))
