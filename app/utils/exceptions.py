"""
Custom exceptions

Provide a small hierarchy of exceptions with optional contextual attributes
(useful for logging and programmatic handling).
"""

from __future__ import annotations

from typing import Any, Optional, Dict


class BaseException(Exception):
    """Base exception.

    Subclass this for any error that should be caught by higher-level code.
    """

    def __init__(self, message: Optional[str] = None, *, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Args:
            message: Human-readable error message.
            context: Optional dict with extra programmatic context (e.g. url, status_code).
        """
        super().__init__(message or self.__class__.__name__)
        self.message = message or self.__class__.__name__
        self.context = context or {}

    def __str__(self) -> str:
        ctx = f" context={self.context}" if self.context else ""
        return f"{self.__class__.__name__}: {self.message}{ctx}"

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation useful for logging/metrics."""
        return {"type": self.__class__.__name__, "message": self.message, "context": self.context}


class ParseError(BaseException):
    """Raised when parsing (XML/JSON) fails.

    Example context keys:
      - source: which file or payload failed (e.g. 'xunit.xml')
      - line/column: parser position if available
      - original_exception: underlying parser error
    """

    def __init__(self, message: Optional[str] = None, *, source: Optional[str] = None,
                 line: Optional[int] = None, column: Optional[int] = None,
                 original_exception: Optional[BaseException] = None) -> None:
        context = {}
        if source:
            context["source"] = source
        if line is not None:
            context["line"] = line
        if column is not None:
            context["column"] = column
        if original_exception is not None:
            context["original_exception"] = repr(original_exception)

        super().__init__(message or "Failed to parse input", context=context)
        self.source = source
        self.line = line
        self.column = column
        self.original_exception = original_exception
