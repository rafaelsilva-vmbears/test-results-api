
import pytest
from unittest.mock import Mock, create_autospec
from datetime import datetime

from app.application.use_cases.execution.get_list_executions_use_case import GetListExecutionsUseCase
from app.domain.interfaces.execution_repository_interface import ExecutionRepositoryInterface

@pytest.fixture
def mock_repo():
    return create_autospec(ExecutionRepositoryInterface, instance=True)

@pytest.fixture
def sut(mock_repo):
    return GetListExecutionsUseCase(repository=mock_repo)

class TestGetListExecutionsUseCase:

    def test_should_pass_filters_to_repository(self, sut, mock_repo):
        """
        GIVEN valid filters
        WHEN execute is called
        THEN repository is called with correct arguments
        """
        start = datetime(2023, 1, 1)
        end = datetime(2023, 1, 31)
        mock_repo.find_executions.return_value = ["exec1", "exec2"]

        result = sut.execute("ProjectX", "Dev", start, end, limit=10)

        mock_repo.find_executions.assert_called_once_with(
            "projectx", "dev", start, end, 10
        )
        assert result == ["exec1", "exec2"]

    def test_should_default_limit_to_50(self, sut, mock_repo):
        """
        GIVEN no limit specified
        WHEN execute is called
        THEN default limit is used
        """
        sut.execute("p", "e", datetime.now(), datetime.now())

        args = mock_repo.find_executions.call_args.args
        assert args[4] == 50
