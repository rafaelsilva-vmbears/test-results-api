"""
This file defines a FastAPI application for managing test execution results.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.domain.errors.exceptions.invalid_date_range_error import InvalidDateRangeError
from app.api.v1.routes import executions, metrics, xml, xml_execution, health, main, projects
from app.api.handlers.error_handler import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
    invalid_date_range_exception_handler
)
from app.infrastructure.logging.logging_config import initialize_logging, get_logger
from app.infrastructure.db.mongo_database_connection import MongoDatabaseConnection
from app.infrastructure.db.mongomock_database_connection import MongomockDatabaseConnection
from app.infrastructure.db.adapters.mongo_adapter import MongoDatabaseAdapter
from app.api.v1.routes.admin import admin_api_keys

load_dotenv()

initialize_logging()
logger = get_logger(__name__)


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.db_connection.connect()
    logger.info("MongoDB connected")
    yield
    # Shutdown
    app.state.db_connection.close_connection()
    logger.info("MongoDB connection closed")

def create_app() -> FastAPI:

    """Creates and configures the FastAPI application instance."""
    app = FastAPI(
        title="Test Results API",
        description="API for storing and returning automated test executions",
        version="1.1.0",
        openapi_url=None,
        lifespan=lifespan,
    )

    #Composition root: cria uma vez e reutiliza no app todo
    use_mongomock = os.getenv("USE_MONGOMOCK", "").lower() in ("true", "1", "yes")
    mongo_uri = os.getenv("MONGO_URI", "").strip()

    if use_mongomock or not mongo_uri:
        logger.info("Using mongomock in-memory database (local development mode)")
        app.state.db_connection = MongomockDatabaseConnection()
    else:
        app.state.db_connection = MongoDatabaseConnection()

    app.state.db_adapter = MongoDatabaseAdapter(app.state.db_connection)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Handlers globais
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(InvalidDateRangeError, invalid_date_range_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Rotas
    app.include_router(executions.router)
    app.include_router(main.router)
    app.include_router(health.router)
    app.include_router(metrics.router)
    app.include_router(xml.router)
    app.include_router(xml_execution.router)
    app.include_router(projects.router)
    app.include_router(admin_api_keys.router)

    # Schema interno com segurança X-API-Key e modelos
    @app.get("/openapi.json", include_in_schema=False)
    async def internal_openapi():
        openapi_schema = app.openapi()
        openapi_schema["components"]["securitySchemes"] = {
            "APIKeyHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "Insira sua API Key de time ou a MASTER_KEY para operações administrativas.",
            }
        }

        for path in openapi_schema.get("paths", {}).values():
            for operation in path.values():
                operation.setdefault("security", [{"APIKeyHeader": []}])

        return JSONResponse(content=openapi_schema)

    # Swagger público
    @app.get("/docs", include_in_schema=False)
    async def get_swagger_documentation():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="Test Results API - Swagger UI",
        )

    return app
