import secrets
from typing import List
from app.domain.entities.api_key_entity import ApiKey
from app.domain.interfaces.api_key_repository_interface import ApiKeyRepositoryInterface
from app.application.dtos.api_key_dtos import ApiKeyCreateRequest, ApiKeyResponse, ApiKeyUpdateRequest

from fastapi import HTTPException, status

class GenerateApiKeyUseCase:
    def __init__(self, repository: ApiKeyRepositoryInterface):
        self.repository = repository

    def execute(self, request: ApiKeyCreateRequest) -> ApiKeyResponse:
        normalized_team_name = request.team_name.lower().strip()

        existing_key = self.repository.get_by_team_name(normalized_team_name)
        if existing_key:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Team '{normalized_team_name}' already has an active API Key."
            )

        key = secrets.token_urlsafe(32)
        api_key = ApiKey(
            key=key,
            team_name=normalized_team_name,
            permissions=request.permissions
        )
        self.repository.save(api_key)
        # Note: save() logic in MongoApiKeyRepository sets the ID on the entity if instance is passed
        return self._map_to_response(api_key)

    def _map_to_response(self, entity: ApiKey) -> ApiKeyResponse:
        return ApiKeyResponse(
            id=entity.id,
            key=entity.key,
            team_name=entity.team_name,
            permissions=entity.permissions,
            created_at=entity.created_at,
            is_active=entity.is_active
        )

class RevokeApiKeyUseCase:
    def __init__(self, repository: ApiKeyRepositoryInterface):
        self.repository = repository

    def execute(self, key: str) -> None:
        self.repository.revoke(key)

class ListApiKeysUseCase:
    def __init__(self, repository: ApiKeyRepositoryInterface):
        self.repository = repository

    def execute(self) -> List[ApiKeyResponse]:
        keys = self.repository.list_keys()
        return [self._map_to_response(k) for k in keys]

    def _map_to_response(self, entity: ApiKey) -> ApiKeyResponse:
        return ApiKeyResponse(
            id=entity.id,
            key=entity.key,
            team_name=entity.team_name,
            permissions=entity.permissions,
            created_at=entity.created_at,
            is_active=entity.is_active
        )

class UpdateApiKeyUseCase:
    def __init__(self, repository: ApiKeyRepositoryInterface):
        self.repository = repository

    def execute(self, key: str, request: ApiKeyUpdateRequest) -> None:
        updated = self.repository.update_permissions(key, request.permissions)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API Key not found or inactive."
            )
