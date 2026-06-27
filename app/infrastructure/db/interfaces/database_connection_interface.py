# app/infrastructure/db/interfaces/database_connection_interface.py
from abc import ABC, abstractmethod
from typing import Any


class DatabaseConnectionInterface(ABC):
    """Defines the interface for database connection operations."""
    @abstractmethod
    def connect(self) -> None:
        """Establishes a connection to the database."""

    @abstractmethod
    def close_connection(self) -> None:
        """Closes the database connection."""

    @abstractmethod
    def get_collection(self, collection_name: str) -> Any:
        """Retrieves a specific collection from the database by its name."""

    @abstractmethod
    def get_database_stats(self) -> dict:
        """Retrieves statistics about the database as a dictionary."""
