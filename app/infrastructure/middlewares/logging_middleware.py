"""
This module defines the LoggingMiddleware class for FastAPI applications.
It logs details of incoming requests and outgoing responses, including method,
URL, client information, headers, status code, and processing time.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.infrastructure.logging.logging_config import get_logger


logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logar todas as requisições e respostas HTTP."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # logger.info(
        #     "REQUEST: %s %s Client: %s:%s Headers: %s",
        #     request.method,
        #     request.url.path,
        #     request.client.host,
        #     request.client.port,
        #     dict(request.headers)
        # )

        try:
            # Processa a requisição
            response = await call_next(request)

            # Calcula o tempo de processamento
            process_time = time.time() - start_time

            logger.info(
                "RESPONSE: %s %s Status: %s ProcessTime: %.4fs",
                request.method,
                request.url.path,
                response.status_code,
                process_time
            )

            return response

        except Exception as e:
            # Calcula o tempo de processamento mesmo em caso de erro
            process_time = time.time() - start_time

            logger.error(
                "ERROR: %s %s Exception: %s ProcessTime: %.4fs",
                request.method,
                request.url.path,
                str(e),
                process_time
            )

            # Re-levanta a exceção para que os handlers apropriados a tratem
            raise e
