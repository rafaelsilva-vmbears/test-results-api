"""
This module defines custom exception handlers
for a FastAPI application to standardize error responses.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.format_error_response import format_error_response
from app.domain.errors.exceptions.invalid_date_range_error import InvalidDateRangeError


def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles RequestValidationError exceptions and returns a standardized error response."""
    return JSONResponse(
        status_code=422,
        content=format_error_response(
            "ValidationError",
            str(exc.errors()),
            422,
            str(request.url.path),
        ),
    )


def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles StarletteHTTPException and returns a standardized error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            "HTTPException",
            str(exc.detail),
            exc.status_code,
            str(request.url.path),
        ),
    )


def generic_exception_handler(request: Request, exc: Exception):
    """Handles generic exceptions and returns a standardized error response."""
    return JSONResponse(
        status_code=500,
        content=format_error_response(
            type(exc).__name__,
            str(exc),
            500,
            str(request.url.path),
        ),
    )


def invalid_date_range_exception_handler(request: Request, exc: InvalidDateRangeError):
    """Handler específico para InvalidDateRangeError."""
    return JSONResponse(
        status_code=400,  # ou 400, dependendo da semântica desejada
        content=format_error_response(
            "InvalidDateRangeError",
            str(exc),
            422,
            str(request.url.path),
        ),
    )
