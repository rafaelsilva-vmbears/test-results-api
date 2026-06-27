from typing import List, Optional, Any, Dict
from bson import ObjectId
from app.domain.entities.api_key_entity import ApiKey
from app.domain.interfaces.api_key_repository_interface import ApiKeyRepositoryInterface
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface

class MongoApiKeyRepository(ApiKeyRepositoryInterface):
    def __init__(self, adapter: DatabaseAdapterInterface):
        self.adapter = adapter
        self.collection = "api_keys"

    def save(self, api_key: ApiKey) -> None:
        doc = {
            "key": api_key.key,
            "team_name": api_key.team_name,
            "permissions": api_key.permissions,
            "created_at": api_key.created_at,
            "is_active": api_key.is_active
        }

        if api_key.id:
            self.adapter.find_one_and_update(
                collection=self.collection,
                query={"_id": ObjectId(api_key.id)},
                update={"$set": doc}
            )
        else:
            inserted_id = self.adapter.insert_one(self.collection, doc)
            api_key.id = inserted_id

    def get_by_key(self, key: str) -> Optional[ApiKey]:
        doc = self.adapter.find_one(self.collection, {"key": key})
        if doc:
            return self._map_doc_to_entity(doc)
        return None

    def revoke(self, key: str) -> None:
        self.adapter.find_one_and_update(
            collection=self.collection,
            query={"key": key},
            update={"$set": {"is_active": False}}
        )

    def list_keys(self) -> List[ApiKey]:
        docs = self.adapter.find(self.collection, {})
        return [self._map_doc_to_entity(doc) for doc in docs]

    def get_by_team_name(self, team_name: str) -> Optional[ApiKey]:
        doc = self.adapter.find_one(self.collection, {"team_name": team_name, "is_active": True})
        if doc:
            return self._map_doc_to_entity(doc)
        return None

    def _map_doc_to_entity(self, doc: Dict[str, Any]) -> ApiKey:
        return ApiKey(
            id=doc.get("id", ""),
            key=doc["key"],
            team_name=doc["team_name"],
            permissions=doc.get("permissions", []),
            created_at=doc["created_at"],
            is_active=doc["is_active"]
        )

    def update_permissions(self, key: str, permissions: List[str]) -> bool:
        result = self.adapter.find_one_and_update(
            collection=self.collection,
            query={"key": key, "is_active": True},
            update={"$set": {"permissions": permissions}},
            return_after=True
        )
        return result is not None
