"""MongoDB connection manager implementing DatabaseConnectionInterface."""

import os
import time
from typing import Optional
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.infrastructure.db.interfaces.database_connection_interface import (
    DatabaseConnectionInterface
)
from app.infrastructure.logging.logging_config import get_logger
from app.infrastructure.db.errors.exceptions.database_connection_error import (
    DatabaseConnectionError, CloseDatabaseConnectionError
)

load_dotenv()
logger = get_logger(__name__)


class MongoDatabaseConnection(DatabaseConnectionInterface):
    """Singleton class for managing MongoDB connections."""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.client: Optional[MongoClient] = None
            self.db = None
            self.db_name = None
            self._initialized = True
            self.max_retries = int(os.getenv("MONGO_MAX_RETRIES", "3"))
            self.retry_delay = int(os.getenv("MONGO_RETRY_DELAY", "2"))

    def _build_connection_uri(self) -> str:
        """Build connection URI prioritizing full MONGO_URI."""
        mongo_uri = os.getenv("MONGO_URI")
        if mongo_uri:
            return mongo_uri

        mongo_host = os.getenv("MONGO_HOST", "localhost")
        mongo_port = os.getenv("MONGO_PORT", "27017")
        db_name = os.getenv("DB_NAME", "test_results")
        username = os.getenv("MONGO_USERNAME")
        password = os.getenv("MONGO_PASSWORD")

        if username and password:
            return f"mongodb://{username}:{password}@{mongo_host}:{mongo_port}/{db_name}"
        return f"mongodb://{mongo_host}:{mongo_port}/{db_name}"

    def connect(self, force_reconnect: bool = False):
        """Establish connection to MongoDB."""
        if self.client is not None and self.is_connected() and not force_reconnect:
            logger.info("MongoDB already connected")
            return

        if self.client is not None:
            self.close_connection()

        self.db_name = os.getenv("DB_NAME", "test_results")

        for attempt in range(1, self.max_retries + 1):
            try:
                uri = self._build_connection_uri()
                logger.info(
                    f"Connecting to MongoDB (attempt {attempt}/{self.max_retries})")

                self.client = MongoClient(
                    uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=10000)
                self.client.admin.command('ping')
                logger.info("MongoDB connection established")

                self.db = self.client[self.db_name]
                return
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to connect after {self.max_retries} attempts")
                    self.client = None
                    self.db = None
                    raise
            except Exception as e:
                logger.error(f"Unexpected error connecting to MongoDB: {e}")
                self.client = None
                self.db = None
                raise

    def close_connection(self):
        """Close MongoDB connection."""
        if self.client is not None:
            try:
                self.client.close()
                logger.info("MongoDB connection closed")
            except CloseDatabaseConnectionError as e:
                logger.error(f"Error closing MongoDB connection: {e}")
            finally:
                self.client = None
                self.db = None

    def is_connected(self) -> bool:
        """Check if MongoDB is connected."""
        if self.client is None:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except DatabaseConnectionError:
            return False

    def get_collection(self, collection_name: str):
        """Get collection from database."""
        if self.db is None:
            try:
                self.connect(force_reconnect=True)
            except Exception as e:
                logger.error(f"Failed to reconnect to MongoDB: {e}")
                raise ConnectionError("Could not connect to database") from e

        if self.db is None:
            raise ConnectionError("Database not available")

        return self.db.get_collection(collection_name)

    def get_database_stats(self):
        """Get database statistics."""
        if self.db is None:
            raise ConnectionError("Database not connected")
        try:
            return self.db.command("dbStats")
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            raise

    def __enter__(self):
        """Context manager support."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support."""
        self.close_connection()
