"""Root endpoint for the API."""

import time
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["main"])

"""
Alterei o include para False visto que a documentação abaixo é redundante e necessita atualizar
toda vez que um novo endpoint for criado. Verificar se isso é realmente necessário, visto que já
existem dois endpoints para monitorar a api e o banco.
"""
@router.get("/", include_in_schema=False)
async def root_endpoint():
    """Friendly root endpoint with API information."""
    payload = {
        "message": "Test Results API",
        "description": "API for storing and returning automated test executions",
        "version": "1.1.0",
        "status": "ok",
        "endpoints": {
            "health": {
                "live": "/health/live",
                "ready": "/health/ready"
            },
            "executions": {
                "create": "POST /executions",
                "list": "GET /executions"
            },
            "metrics": {
                "summary": "GET /metrics/summary",
                "failures": "GET /metrics/failures"
            },
            "xml": {
                "process": "POST /xml/process",
                "process_and_save": "POST /xml-execution/process-and-save"
            }
        },
        "documentation": "/docs",
        "timestamp": int(time.time())
    }
    return JSONResponse(status_code=200, content=payload)
