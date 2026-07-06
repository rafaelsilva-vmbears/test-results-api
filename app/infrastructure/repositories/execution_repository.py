from typing import Optional, List
from datetime import datetime, timezone
from bson.objectid import ObjectId
from bson.errors import InvalidId

from app.domain.interfaces.execution_repository_interface import ExecutionRepositoryInterface
from app.domain.entities.execution_entity import ExecutionEntity
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface
from app.infrastructure.db.mappers.mappers import entity_to_doc, doc_to_entity

from app.infrastructure.logging.logging_config import initialize_logging, get_logger
from app.utils.utilities import normalize_project_id, normalize_project_name

initialize_logging()
logger = get_logger(__name__)


class ExecutionRepository(ExecutionRepositoryInterface):
    """Execution repository for managing execution data in the database."""

    def __init__(self, adapter: DatabaseAdapterInterface):
        self.adapter = adapter
        self.runs_collection = "runs"
        self.counters_collection = "counters"
        self.projects_collection = "projects"

    def get_next_run_number(self, project: str, environment: str) -> int:
        project = normalize_project_id(project)
        environment = environment.lower()

        if environment not in ("uat", "rc", 'unit'):
            raise ValueError(f"Invalid environment: {environment}")

        query = {"_id": project}
        update = {"$inc": {f"seq.{environment}": 1}}

        doc = self.adapter.find_one_and_update(
            self.counters_collection,
            query,
            update,
            upsert=True,
            return_after=True,
        )

        seq_obj = (doc or {}).get("seq", {})
        return int(seq_obj.get(environment, 1))

    def insert_execution(self, execution: ExecutionEntity) -> str:
        """Inserts an execution entity into runs and upserts the project into projects."""
        # Garante normalização antes de persistir
        execution.project = normalize_project_id(execution.project)
        if execution.environment:
            execution.environment = execution.environment.lower()
        else:
            execution.environment = ""

        entity = entity_to_doc(execution)
        inserted_id = self.adapter.insert_one(self.runs_collection, entity)

        # Upsert do projeto
        project_id = execution.project  # já normalizado
        project_name = normalize_project_name(project_id)
        now = datetime.now(timezone.utc)

        update_doc = {
            "$setOnInsert": {
                "name": project_name,
                "created_at": now,
            },
            "$set": {
                "last_seen_at": now,
            },
            "$inc": {
                "total_runs": 1,
            },
        }

        # ✅ Mantém lista de environments viva (sem duplicar)
        if execution.environment:
            update_doc["$addToSet"] = {"environments": execution.environment}

        self.adapter.get_collection(self.projects_collection).update_one(
            {"_id": project_id},
            update_doc,
            upsert=True,
        )

        return inserted_id

    def find_executions(
        self,
        project: str,
        environment: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[ExecutionEntity]:
        """Finds executions for a given project and environment within a date range."""

        project = normalize_project_id(project)
        environment = environment.lower()

        query = {
            "project": project,
            "environment": environment,
        }
        if start_dt and end_dt:
            query["created_at"] = {"$gte": start_dt, "$lte": end_dt}

        docs = self.adapter.find(
            collection=self.runs_collection,
            query=query,
            sort=[("created_at", -1)],
            limit=limit,
        )

        entities: List[ExecutionEntity] = []
        for d in docs:
            entities.append(doc_to_entity(d))


        logger.info(
            "Find executions for project: %s, start_dt: %s, end_dt: %s, limit: %d",
            project,
            start_dt,
            end_dt,
            limit,
        )

        return entities

    def get_execution_by_id(self, execution_id: str) -> ExecutionEntity | None:
        """Retrieves an execution entity by its ID."""
        try:
            object_id = ObjectId(execution_id)
        except InvalidId:
            logger.warning("Invalid ObjectId format for ID: %s", execution_id)
            return None

        query = {"_id": object_id}
        doc = self.adapter.find_one(
            collection=self.runs_collection,
            query=query,
        )

        if not doc:
            logger.info("Execution not found in DB for ID: %s", execution_id)
            return None

        # Mapeia o dicionário retornado pelo adapter para ExecutionEntity
        return doc_to_entity(doc)
