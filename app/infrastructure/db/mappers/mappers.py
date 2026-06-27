""" Mapper to convert between dictionary representations and ExecutionEntity objects. """

from typing import Dict, Any
from datetime import datetime
from app.domain.entities.execution_entity import ExecutionEntity
from app.infrastructure.db.models.execution_document import ExecutionDocument


def doc_to_entity(doc: ExecutionDocument) -> ExecutionEntity:
    """ Converts a dictionary representation to an ExecutionEntity object. """
    doc_id = doc.get("id")
    if doc_id is None:
        doc_id = doc.get("_id")

    if doc_id is not None:
        id_str = str(doc_id)
    else:
        # Fallback caso não tenha id
        id_str = "unknown"

    # Tratar a data
    created_at = doc.get("created_at")
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at)
        except ValueError:
            created_at = datetime.now()

    return ExecutionEntity(
        id=id_str,
        project=doc.get("project"),
        source=doc.get("source"),
        environment=doc.get("environment"),
        run_number=doc.get("run_number"),
        created_at=created_at,
        execution_date=doc.get("execution_date", created_at),
        total=doc.get("total", 0),
        failures=doc.get("failures", 0),
        skipped=doc.get("skipped", 0),
        passed=doc.get("passed"),
        pass_rate=doc.get("pass_rate", 0.0),
        failure_rate=doc.get("failure_rate", 0.0),
        skipped_rate=doc.get("skipped_rate", 0.0),
        tests=doc.get("test_results"),
        failed_cases=doc.get("failed_cases"),
    )


def entity_to_doc(entity: ExecutionEntity) -> ExecutionDocument:
    """ Converts an ExecutionEntity object to a dictionary representation. """
    doc = {
        "project": entity.project,
        "environment": entity.environment,
        "run_number": entity.run_number,
        "created_at": entity.created_at,
        "execution_date": entity.execution_date or entity.created_at,
        "total": entity.total,
        "failures": entity.failures,
        "skipped": entity.skipped,
        "passed": entity.passed,
        "pass_rate": entity.pass_rate,
        "failure_rate": entity.failure_rate,
        "skipped_rate": entity.skipped_rate,
        "test_results": entity.tests,
        "failed_cases": entity.failed_cases,
    }
    if entity.id and entity.id != "unknown":
        doc["_id"] = entity.id
    return doc
