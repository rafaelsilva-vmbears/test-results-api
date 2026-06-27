"""
This module provides a utility function to standardize error responses for FastAPI applications.
"""
from datetime import datetime


def format_error_response(error_type: str, message: str, status_code: int, path: str):
    """Função utilitária para padronizar respostas de erro."""
    return {
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "path": path,
        }
    }
