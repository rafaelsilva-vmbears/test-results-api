
import pytest
from unittest.mock import Mock, create_autospec, ANY
from datetime import datetime

from app.application.use_cases.execution.create_exections_use_case import CreateExecutionUseCase
from app.domain.interfaces.execution_repository_interface import ExecutionRepositoryInterface
from app.application.dtos.execution_dto import CreateExecutionDTO
from app.domain.entities.execution_entity import ExecutionEntity

@pytest.fixture
def mock_repo():
    return create_autospec(ExecutionRepositoryInterface, instance=True)

@pytest.fixture
def sut(mock_repo):
    return CreateExecutionUseCase(repository=mock_repo)

class TestCreateExecutionUseCase:

    def test_should_create_execution_successfully(self, sut, mock_repo):
        """
        GIVEN a valid payload
        WHEN execute is called
        THEN it should get the next run number and persist the entity
        """
        # Arrange
        project = "Teste"
        env = "Staging"
        mock_repo.get_next_run_number.return_value = 42
        mock_repo.insert_execution.return_value = "db-id-123"

        payload = CreateExecutionDTO(
            source="Pipeline",
            created_at=datetime(2023, 1, 1),
            total=10,
            failures=1,
            skipped=0,
            passed=9,
            pass_rate=90.0,
            failure_rate=10.0,
            skipped_rate=0.0,
            tests=[],
            failed_cases=[]
        )

        # Act
        result = sut.execute(payload, project, env)

        # Assert
        # 1. Check run number generation
        mock_repo.get_next_run_number.assert_called_once_with("Teste", "Staging")

        # 2. Check persistence
        mock_repo.insert_execution.assert_called_once()
        inserted_entity = mock_repo.insert_execution.call_args[0][0]

        assert isinstance(inserted_entity, ExecutionEntity)
        assert inserted_entity.project == "teste"  # Normalized
        assert inserted_entity.environment == "staging"
        assert inserted_entity.run_number == 42
        assert inserted_entity.source == "pipeline"

        # 3. Check result
        assert result.id == "db-id-123"
        assert result.run_number == 42
