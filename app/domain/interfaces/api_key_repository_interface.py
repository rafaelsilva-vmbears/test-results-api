from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.api_key_entity import ApiKey

class ApiKeyRepositoryInterface(ABC):
    @abstractmethod
    def save(self, api_key: ApiKey) -> None:
        pass

    @abstractmethod
    def get_by_key(self, key: str) -> Optional[ApiKey]:
        pass

    @abstractmethod
    def revoke(self, key: str) -> None:
        pass

    @abstractmethod
    def list_keys(self) -> List[ApiKey]:
        pass

    @abstractmethod
    def get_by_team_name(self, team_name: str) -> Optional[ApiKey]:
        pass

    @abstractmethod
    def update_permissions(self, key: str, permissions: List[str]) -> bool:
        """Updates permissions for an API Key. Returns True if found and updated."""
        pass
