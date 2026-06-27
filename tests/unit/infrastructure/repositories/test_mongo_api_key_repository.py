import pytest
from unittest.mock import Mock
from datetime import datetime
from bson import ObjectId

from app.infrastructure.repositories.mongo_api_key_repository import MongoApiKeyRepository
from app.domain.entities.api_key_entity import ApiKey

class TestMongoApiKeyRepositoryUnit:

    @pytest.fixture
    def mock_adapter(self):
        return Mock()

    @pytest.fixture
    def repository(self, mock_adapter):
        return MongoApiKeyRepository(mock_adapter)

    def test_save_update_existing_key(self, repository, mock_adapter):
        # Test saving a key that already has an ID (should trigger update)
        api_key = ApiKey(
            id="507f1f77bcf86cd799439011",
            key="test-key",
            team_name="test-team",
            permissions=["READ"],
            created_at=datetime.now(),
            is_active=True
        )

        repository.save(api_key)

        mock_adapter.find_one_and_update.assert_called_once()
        args = mock_adapter.find_one_and_update.call_args
        assert args.kwargs['collection'] == "api_keys"
        assert args.kwargs['query'] == {"_id": ObjectId(api_key.id)}
        assert "$set" in args.kwargs['update']
        assert args.kwargs['update']["$set"]["key"] == "test-key"

    def test_save_new_key(self, repository, mock_adapter):
        # Test saving a new key (should trigger insert_one)
        api_key = ApiKey(
            id=None,
            key="new-key",
            team_name="new-team",
            permissions=[],
            created_at=datetime.now(),
            is_active=True
        )
        mock_adapter.insert_one.return_value = "new_id_123"

        repository.save(api_key)

        mock_adapter.insert_one.assert_called_once()
        assert api_key.id == "new_id_123"

    def test_get_by_key_not_found(self, repository, mock_adapter):
        mock_adapter.find_one.return_value = None
        result = repository.get_by_key("missing-key")
        assert result is None

    def test_update_permissions_success(self, repository, mock_adapter):
        mock_adapter.find_one_and_update.return_value = {"key": "k", "permissions": ["w"]}
        success = repository.update_permissions("k", ["WRITE"])
        assert success is True

    def test_update_permissions_not_found(self, repository, mock_adapter):
        mock_adapter.find_one_and_update.return_value = None
        success = repository.update_permissions("missing", ["WRITE"])
        assert success is False
