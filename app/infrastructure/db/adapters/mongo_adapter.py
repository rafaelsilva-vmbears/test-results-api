"""MongoDB adapter implementing DatabaseAdapterInterface."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pymongo import ReturnDocument
from app.infrastructure.db.interfaces.database_adapter_interface import (
    DatabaseAdapterInterface
)
from app.infrastructure.db.interfaces.database_connection_interface import (
    DatabaseConnectionInterface
)
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


class MongoDatabaseAdapter(DatabaseAdapterInterface):
    """Implementation of DatabaseAdapterInterface for MongoDB."""

    def __init__(self, db_connection: DatabaseConnectionInterface):
        self.db_connection = db_connection

    def _to_jsonable(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to JSON serializable format."""
        if doc is None:
            return doc

        out = dict(doc)
        _id = out.pop("_id", None)
        out["id"] = str(_id) if _id is not None else None

        created = out.get("created_at")
        if isinstance(created, str):
            try:
                out["created_at"] = datetime.fromisoformat(created)
            except (ValueError, TypeError):
                pass

        return out

    def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert document and return ID."""
        coll = self.db_connection.get_collection(collection)
        result = coll.insert_one(document)
        inserted_id = str(result.inserted_id)
        logger.debug("Document inserted in collection %s with ID: %s",
                     collection, inserted_id)
        return inserted_id

    def find_one_and_update(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
        return_after: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Find and update document, return before/after."""
        coll = self.db_connection.get_collection(collection)
        doc = coll.find_one_and_update(
            query,
            update,
            upsert=upsert,
            return_document=ReturnDocument.AFTER if return_after else ReturnDocument.BEFORE
        )
        result = self._to_jsonable(doc) if doc else None
        logger.debug("find_one_and_update in %s with filter %s: %s",
                     collection, query, "found" if result else "not found")
        return result

    def find(
        self,
        collection: str,
        query: Dict[str, Any],
        sort: Optional[list] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find documents in collection."""
        coll = self.db_connection.get_collection(collection)
        cursor = coll.find(query)

        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)

        documents = list(cursor)
        logger.debug("Found %d documents in collection %s",
                     len(documents), collection)
        return [self._to_jsonable(doc) for doc in documents]

    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        coll = self.db_connection.get_collection(collection)
        cursor = coll.find_one(query)
        return self._to_jsonable(cursor) if cursor else None

    def get_collection(self, collection: str) -> Any:
        """Get collection reference."""
        return self.db_connection.get_collection(collection)
