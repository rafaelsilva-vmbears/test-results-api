from fastapi import APIRouter, Depends, status, Request
from typing import List
from app.infrastructure.security.security import verify_master_key
from app.application.dtos.api_key_dtos import ApiKeyCreateRequest, ApiKeyResponse, ApiKeyUpdateRequest
from app.application.use_cases.security.api_key_use_cases import (
    GenerateApiKeyUseCase,
    RevokeApiKeyUseCase,
    ListApiKeysUseCase,
    UpdateApiKeyUseCase
)
from app.infrastructure.repositories.mongo_api_key_repository import MongoApiKeyRepository

router = APIRouter(
    prefix="/admin/api-keys",
    tags=["Admin - API Keys"],
    dependencies=[Depends(verify_master_key)]
)

def get_repository(request: Request) -> MongoApiKeyRepository:
    adapter = request.app.state.db_adapter
    return MongoApiKeyRepository(adapter)

@router.post("", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    request: ApiKeyCreateRequest,
    req: Request
):
    repo = get_repository(req)
    use_case = GenerateApiKeyUseCase(repo)
    return use_case.execute(request)

@router.get("", response_model=List[ApiKeyResponse])
def list_api_keys(req: Request):
    repo = get_repository(req)
    use_case = ListApiKeysUseCase(repo)
    return use_case.execute()

@router.put("/{key}", status_code=status.HTTP_204_NO_CONTENT)
def update_api_key_permissions(
    key: str,
    request: ApiKeyUpdateRequest,
    req: Request
):
    repo = get_repository(req)
    use_case = UpdateApiKeyUseCase(repo)
    use_case.execute(key, request)

@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(key: str, req: Request):
    repo = get_repository(req)
    use_case = RevokeApiKeyUseCase(repo)
    use_case.execute(key)
