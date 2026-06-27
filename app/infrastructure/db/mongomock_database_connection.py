"""In-memory MongoDB connection using mongomock for local development."""

import os
from typing import Optional
import mongomock
from app.infrastructure.db.interfaces.database_connection_interface import (
    DatabaseConnectionInterface
)
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


class MongomockDatabaseConnection(DatabaseConnectionInterface):
    """In-memory MongoDB connection using mongomock.

    Implements DatabaseConnectionInterface so it can be used as a
    drop-in replacement for MongoDatabaseConnection.  All data lives
    in process memory and is lost when the application stops.

    Activate via USE_MONGOMOCK=true or by leaving MONGO_URI empty.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.client: Optional[mongomock.MongoClient] = None
            self.db = None
            self.db_name = os.getenv("DB_NAME", "test_results")
            self._initialized = True

    def connect(self, force_reconnect: bool = False):
        """Create an in-memory mongomock connection."""
        if self.client is not None and not force_reconnect:
            logger.info("Mongomock already connected")
            return

        self.client = mongomock.MongoClient()
        self.db = self.client[self.db_name]
        logger.info(
            "Mongomock in-memory connection established (DB: %s) "
            "— data will NOT persist across restarts",
            self.db_name,
        )

    def close_connection(self):
        """Close the mongomock connection."""
        if self.client is not None:
            self.client.close()
            logger.info("Mongomock connection closed")
            self.client = None
            self.db = None

    def is_connected(self) -> bool:
        """Check if mongomock is connected."""
        return self.client is not None

    def get_collection(self, collection_name: str):
        """Get collection from the in-memory database."""
        if self.db is None:
            self.connect()
        return self.db.get_collection(collection_name)

    def get_database_stats(self) -> dict:
        """Return basic stats about the in-memory database."""
        if self.db is None:
            raise ConnectionError("Database not connected")
        collections = self.db.list_collection_names()
        return {
            "db": self.db_name,
            "engine": "mongomock (in-memory)",
            "collections": len(collections),
            "collection_names": collections,
        }

    def __enter__(self):
        """Context manager support."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support."""
        self.close_connection()
