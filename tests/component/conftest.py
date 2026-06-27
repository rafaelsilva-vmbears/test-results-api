
import pytest
import mongomock
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_db_adapter
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface

@pytest.fixture
def mock_mongo_adapter():
    """Returns a mock adapter connected to a temporary mongomock database."""
    adapter = Mock(spec=DatabaseAdapterInterface)
    client = mongomock.MongoClient()
    db = client.test_db

    # Simulating Adapter methods using mongomock
    def get_collection(name):
        return db[name]

    # Map CRUD methods if necessary for the controller flow
    def insert_one(col_name, data):
        return str(db[col_name].insert_one(data).inserted_id)

    def find_one_and_update(collection, query, update, upsert=False, return_after=False):
        return db[collection].find_one_and_update(
            query, update, upsert=upsert, return_document=return_after
        )

    def find(collection, query, projection=None, sort=None, limit=0, skip=0):
        # Mongomock cursor support
        cursor = db[collection].find(query, projection)
        if sort:
            cursor.sort(sort)
        if skip:
            cursor.skip(skip)
        if limit:
            cursor.limit(limit)
        return list(cursor)

    def find_one(collection, query, projection=None):
        return db[collection].find_one(query, projection)

    adapter.get_collection.side_effect = get_collection
    adapter.insert_one.side_effect = insert_one
    adapter.find_one_and_update.side_effect = find_one_and_update
    adapter.find.side_effect = find
    adapter.find_one.side_effect = find_one

    return adapter

@pytest.fixture
def client(mock_mongo_adapter):
    """
    Returns a TestClient with overridden database dependecies.
    This ensures no real DB connection is attempted.
    """
    # 1. Override the get_db_adapter dependency
    app.dependency_overrides[get_db_adapter] = lambda: mock_mongo_adapter

    # 2. Mock startup events to prevent real connection
    # Note: app.state.db_connection is initialized in create_app, so we just mock its connect method
    original_connect = None
    original_close = None
    if hasattr(app.state, "db_connection"):
        original_connect = app.state.db_connection.connect
        original_close = app.state.db_connection.close_connection
        app.state.db_connection.connect = Mock()
        app.state.db_connection.close_connection = Mock()

    with TestClient(app) as test_client:
        yield test_client

    # Teardown
    app.dependency_overrides.clear()

    # Restore original methods
    if hasattr(app.state, "db_connection"):
        if original_connect:
            app.state.db_connection.connect = original_connect
        if original_close:
            app.state.db_connection.close_connection = original_close
