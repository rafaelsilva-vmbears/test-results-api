"""This module provides the DatabaseConnection class,
which serves as a wrapper around a database connection implementation."""

from dotenv import load_dotenv
from app.infrastructure.db.interfaces.database_connection_interface import (
    DatabaseConnectionInterface)
from app.infrastructure.logging.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


class DatabaseConnection:
    """This class provides a wrapper around a database connection implementation,
    offering methods for connecting, closing, and interacting with the database."""

    def __init__(self, database_connection: DatabaseConnectionInterface):
        self.database_connection = database_connection

    def connect(self):
        """Establishes a connection to the database."""
        return self.database_connection.connect()

    def close_connection(self):
        """Closes the connection to the database."""
        return self.database_connection.close_connection()

    def get_collection(self, collection_name: str):
        """Retrieves a collection from the database by its name."""
        return self.database_connection.get_collection(collection_name)

    def get_database_stats(self):
        """Retrieves statistics about the database."""
        return self.database_connection.get_database_stats()
