"""This module defines Pydantic schemas for validating and
structuring data related to test execution results.
"""

# Adicionado Union para tipos mais flexíveis
from typing import List, Optional, Dict, Union
from datetime import datetime
from pydantic import BaseModel, Field


class TestSchema(BaseModel):
    """Represents a single test case with its details such as name,
    status, execution time, and an optional message."""
    name: str
    status: str
    time: Optional[float] = None
    message: Optional[str] = None
    classname: Optional[str] = None
    run_number: int = 0


class SummaryModel(BaseModel):
    """Aggregates test results into total, failures, skipped, and passed counts."""
    total: int
    failures: int
    skipped: int
    passed: Optional[int] = None


class ExecutionCreateSchema(BaseModel):
    """Defines the structure for creating a new execution,
    including test counts, rates, execution time, and source."""
    total: int
    passed: Optional[int] = None
    failures: int
    errors: Optional[int] = None
    skipped: int
    pass_rate: float
    failure_rate: float
    skipped_rate: float
    time: Optional[float] = None
    source: str = Field(..., description="Fonte dos testes",
                        json_schema_extra={"example": "xml"})  # Corrigido: obrigatório e string
    tests: List[TestSchema]
    failed_cases: List[TestSchema]
    created_at: datetime = Field(..., json_schema_extra={"example": "2023-10-01T12:00:00Z"})
    execution_date: Optional[datetime] = Field(None, json_schema_extra={"example": "2023-10-01T12:00:00Z"})


class CreateExecutionResponseSchema(BaseModel):
    """Defines the response structure after creating an execution, containing the execution id."""
    id: str


class ExecutionResponseSchema(BaseModel):
    """Defines the structure for retrieving execution details,
    including metadata and aggregated results."""
    message: Optional[str] = None  # Adicionado default None
    project: Optional[str] = None
    environment: Optional[str] = None
    run_number: Optional[int] = None  # Pode ser None se não for encontrado
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    execution_date: Optional[datetime] = None
    total: Optional[int] = None
    failures: Optional[int] = None
    skipped: Optional[int] = None
    passed: Optional[int] = None
    pass_rate: Optional[float] = None
    failure_rate: Optional[float] = None
    skipped_rate: Optional[float] = None
    tests: Optional[List[TestSchema]] = None
    failed_cases: Optional[List[TestSchema]] = None


class ExecutionListItemSchema(BaseModel):
    """Represents a simplified execution summary for list views."""
    project: str
    environment: str
    run_number: int
    id: str
    created_at: datetime
    execution_date: Optional[datetime] = None
    total: int
    failures: int
    skipped: int
    passed: Optional[int] = None
    pass_rate: float
    failure_rate: float
    skipped_rate: float
    tests: Optional[List[TestSchema]] = None
    failed_cases: Optional[List[TestSchema]] = None
    # Adicionado 'source' para compatibilidade com ExecutionEntity
    source: Optional[str] = None


class ErrorDetail(BaseModel):
    """Defines the structure for detailed error information,
    including type, message, status code, timestamp, and path."""
    type: str
    message: str
    status_code: int
    timestamp: datetime
    path: str


class ErrorResponseSchema(BaseModel):
    """Defines a standard error response format,
    including error type, message, status code, timestamp, and path."""
    error: ErrorDetail = Field(  # Usando o novo schema ErrorDetail
        ...,
        json_schema_extra={
            "example": {
                "type": "ValidationError",
                "message": "Campo 'project' é obrigatório.",
                "status_code": 400,
                "timestamp": "2025-10-13T12:44:22Z",
                "path": "/executions"
            }
        }
    )
