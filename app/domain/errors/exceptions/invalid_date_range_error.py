"""
This module defines the InvalidDateRangeError exception,
which is raised when a date range is invalid (end date before start date).
"""


class InvalidDateRangeError(Exception):
    """Exceção lançada quando o intervalo de datas é inválido."""

    def __init__(self, message: str = "End date cannot be earlier than start date."):
        self.message = message
        super().__init__(self.message)
