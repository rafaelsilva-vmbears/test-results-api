
import pytest
import mongomock
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.infrastructure.db.adapters.mongo_adapter import MongoDatabaseAdapter

@pytest.fixture
def mock_mongo_client():
    return mongomock.MongoClient()

@pytest.fixture
def mock_db_connection(mock_mongo_client):
    """
    Mocks the DatabaseConnectionInterface to return a mongomock client.
    """
    connection = Mock()
    connection.client = mock_mongo_client
    connection.db = mock_mongo_client.test_db

    # Mock get_collection to return mongomock collection
    def get_collection(name):
        return connection.db[name]

    connection.get_collection.side_effect = get_collection

    # Mock connect/close to do nothing
    connection.connect = Mock()
    connection.close_connection = Mock()
    return connection

@pytest.fixture
def app_with_mock_db(mock_db_connection):
    """
    Creates the app and replaces the DB connection with the mock.
    """
    # Create app normally
    app = create_app()

    # Replace the connection singleton/state with our mock
    app.state.db_connection = mock_db_connection
    # Re-initialize adapter with the mock connection to ensure it uses the mongomock client
    app.state.db_adapter = MongoDatabaseAdapter(mock_db_connection)

    return app

@pytest.fixture
def client(app_with_mock_db):
    """
    Returns a TestClient with the mocked app.
    Also patches MASTER_KEY for admin tests.
    """
    with patch("app.infrastructure.security.security.MASTER_KEY", "test-master-key"):
        with TestClient(app_with_mock_db) as client:
            yield client
