"""Executes the creation of a new execution record."""

from dataclasses import asdict
from app.domain.interfaces.execution_repository_interface import ExecutionRepositoryInterface
from app.application.dtos.execution_dto import CreateExecutionDTO
from app.domain.entities.execution_entity import ExecutionEntity


class CreateExecutionUseCase:
    """ Creates a new execution record based on the provided payload, project, and environment. """

    def __init__(self, repository: ExecutionRepositoryInterface):
        self.repo = repository

    def execute(self, payload: CreateExecutionDTO, project: str, environment) -> ExecutionEntity:
        """Executes the creation of a new execution record."""

        #run_project = f"{project}_{environment}"
        run_number = self.repo.get_next_run_number(project, environment)

        entity = ExecutionEntity(
            id=None,
            project=project.lower(),
            environment=environment.lower(),
            source=payload.source.lower(),
            run_number=run_number,
            created_at=payload.created_at,
            total=payload.total,
            failures=payload.failures,
            skipped=payload.skipped,
            passed=payload.passed,
            pass_rate=payload.pass_rate,
            failure_rate=payload.failure_rate,
            skipped_rate=payload.skipped_rate,
            tests=[asdict(t) for t in payload.tests],
            failed_cases=[asdict(c) for c in payload.failed_cases],
            execution_date=payload.execution_date,
        )

        inserted_id = self.repo.insert_execution(entity)
        entity.id = inserted_id
        return entity
