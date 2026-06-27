"""Defines the DatabaseAdapterInterface for database operations."""
from typing import Protocol, Any, List, Dict, Optional


class DatabaseAdapterInterface(Protocol):
    """Adapter genérico para operações mínimas que o repositório precisa."""

    def insert_one(
            self,
            collection: str,
            document: Dict[str, Any]) -> str:
        """Insere e retorna id como string."""

    def find_one_and_update(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
        return_after: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Opera find_one_and_update; retorna documento atualizado (ou None)."""

    def find(
            self,
            collection: str,
            query: Dict[str, Any],
            sort: Optional[list] = None,
            limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna lista de documentos (já convertidos para tipos JSON-serializáveis)."""

    def find_one(
            self,
            collection: str,
            query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Opera find_one; retorna documento encontrado (ou None)."""

    def get_collection(self, collection: str) -> Any:
        """Retorna o objeto da coleção especificada."""
