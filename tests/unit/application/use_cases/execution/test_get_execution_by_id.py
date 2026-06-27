
import pytest
from unittest.mock import Mock, create_autospec

from app.application.use_cases.execution.get_execution_by_id_use_case import GetExecutionByIdUseCase
from app.domain.interfaces.execution_repository_interface import ExecutionRepositoryInterface
from app.domain.entities.execution_entity import ExecutionEntity

@pytest.fixture
def mock_repo():
    return create_autospec(ExecutionRepositoryInterface, instance=True)

@pytest.fixture
def sut(mock_repo):
    """Subject Under Test"""
    return GetExecutionByIdUseCase(repository=mock_repo)

class TestGetExecutionByIdUseCase:

    def test_should_return_execution_when_found(self, sut, mock_repo):
        """
        GIVEN a valid ID
        WHEN execute is called
        THEN return the execution entity
        """
        # Arrange
        exec_id = "123"
        expected_entity = Mock(spec=ExecutionEntity)
        mock_repo.get_execution_by_id.return_value = expected_entity

        # Act
        result = sut.execute(exec_id)

        # Assert
        mock_repo.get_execution_by_id.assert_called_once_with(exec_id)
        assert result == expected_entity

    def test_should_return_none_when_not_found(self, sut, mock_repo):
        """
        GIVEN a non-existent ID
        WHEN execute is called
        THEN return None and log info (implied)
        """
        exec_id = "999"
        mock_repo.get_execution_by_id.return_value = None

        result = sut.execute(exec_id)

        mock_repo.get_execution_by_id.assert_called_once_with(exec_id)
        assert result is None
