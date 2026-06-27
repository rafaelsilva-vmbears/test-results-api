
import os
import time
from typing import Any, Dict
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import anyio
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)

# TTL (segundos) para cache do resultado da readiness
HEALTH_READY_TTL = int(os.getenv("HEALTH_READY_TTL", "10"))

# Estado de cache e lock para evitar checagens concorrentes
_health_cache: Dict[str, Any] = {
    "last_checked": 0.0,
    "result": {"ok": False, "message": "Not checked yet"},
}
_health_lock = anyio.Lock()

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live() -> JSONResponse:
    """
    Liveness probe.
    Retorna 200 se a aplicação está rodando.
    (não verifica dependências externas)
    """
    payload = {
        "status": "ok",
        "checks": {"app": {"ok": True, "message": "Application running"}},
        "timestamp": int(time.time()),
    }
    return JSONResponse(status_code=200, content=payload)


@router.get("/ready")
async def ready(request: Request) -> JSONResponse:
    """
    Readiness probe com cache:
    - Retorna resultado em cache se dentro do TTL.
    - Executa checagem do DB em thread separado caso o cache esteja expirado.
    - Usa explicitamente client.admin.command("ping") para verificar o MongoDB.
    - Retorna 200 quando a aplicação consegue falar com o DB, 503 caso contrário.
    """
    start = time.time()

    # Retornar cache se ainda válido (rápido)
    now = time.time()
    if now - _health_cache["last_checked"] < HEALTH_READY_TTL:
        result = _health_cache["result"]
        payload = {
            "status": "ok" if result.get("ok") else "unhealthy",
            "checks": {
                "app": {"ok": True, "message": "Application running"},
                "database": result,
            },
            "uptime_seconds": round(time.time() - start, 3),
            "timestamp": int(time.time()),
        }
        status_code = 200 if result.get("ok") else 503
        return JSONResponse(status_code=status_code, content=payload)

    # Evita que múltiplas requisições paralelas causem múltiplas checagens
    async with _health_lock:
        # Re-checar o cache (outro request pode ter atualizado enquanto aguardava)
        now = time.time()
        if now - _health_cache["last_checked"] < HEALTH_READY_TTL:
            result = _health_cache["result"]
            payload = {
                "status": "ok" if result.get("ok") else "unhealthy",
                "checks": {
                    "app": {"ok": True, "message": "Application running"},
                    "database": result,
                },
                "uptime_seconds": round(time.time() - start, 3),
                "timestamp": int(time.time()),
            }
            status_code = 200 if result.get("ok") else 503
            return JSONResponse(status_code=status_code, content=payload)

        # Função síncrona que realiza a checagem do DB (executada em thread)
        def sync_check_db() -> (bool, str):
            """
            Checagem leve usando explicitamente client.admin.command('ping').

            Estratégia:
            - Tenta extrair um objeto que exponha um MongoClient via atributos comuns:
            db_wrapper.database_connection, db_wrapper.db, db_wrapper.database, ou db_wrapper em si.
            - Se encontrar um objeto com atributo `client`, usa client.admin.command('ping').
            - Caso não encontre, tenta obter uma Collection via get_collection() e derivar o client por coll.database.client.
            - Em qualquer exceção retorna False com mensagem descritiva.
            """
            db_wrapper = getattr(request.app.state, "db_wrapper", getattr(request.app.state, "db_connection", None))
            if db_wrapper is None:
                return False, "db_wrapper (or db_connection) not initialized"

            try:
                # candidatos para inspeção (ordem de preferência)
                candidates = [
                    getattr(db_wrapper, "database_connection", None),
                    getattr(db_wrapper, "db", None),
                    getattr(db_wrapper, "database", None),
                    getattr(db_wrapper, "database_connection",
                            None),  # redundante, mas seguro
                    db_wrapper,
                ]

                for candidate in candidates:
                    if candidate is None:
                        continue

                    # Se candidate expõe diretamente `client`
                    client = getattr(candidate, "client", None)
                    if client is not None:
                        try:
                            client.admin.command("ping")
                            return True, "client.admin.command('ping') succeeded (via candidate.client)"
                        except Exception as e:
                            logger.debug(
                                "Ping via candidate.client failed: %s", e)

                    # Se candidate é uma Database ou Collection-like que tem attribute `database` exposing client
                    # Ex.: Collection.database.client
                    try:
                        coll = None
                        # se candidate tem get_collection(), tente obter uma coleção temporária
                        if hasattr(candidate, "get_collection") and callable(getattr(candidate, "get_collection")):
                            try:
                                coll = candidate.get_collection("runs")
                            except Exception as e:
                                logger.debug(
                                    "candidate.get_collection failed: %s", e)
                                coll = None

                        if coll is not None:
                            client_from_coll = getattr(coll, "database", None) and getattr(
                                coll.database, "client", None)
                            if client_from_coll:
                                try:
                                    client_from_coll.admin.command("ping")
                                    return True, "client.admin.command('ping') succeeded (via coll.database.client)"
                                except Exception as e:
                                    logger.debug(
                                        "Ping via coll.database.client failed: %s", e)

                        # fallback: try coll.database.command('ping')
                        try:
                            if hasattr(coll, "database") and hasattr(coll.database, "command"):
                                coll.database.command("ping")
                                return True, "coll.database.command('ping') succeeded"
                        except Exception as e:
                            logger.debug(
                                "coll.database.command('ping') failed: %s", e)
                    except Exception as e:
                        logger.debug("Inspection of candidate failed: %s", e)

                return False, "No client.admin.command('ping') succeeded"
            except Exception as exc:
                logger.exception(
                    "Unexpected exception during DB readiness check: %s", exc)
                return False, f"Unexpected exception: {exc}"

        ok, message = await anyio.to_thread.run_sync(sync_check_db)

        # Atualiza cache com o resultado
        _health_cache["last_checked"] = time.time()
        _health_cache["result"] = {"ok": bool(ok), "message": message}

        # Prepara payload baseado no resultado
        payload = {
            "status": "ok" if ok else "unhealthy",
            "checks": {
                "app": {"ok": True, "message": "Application running"},
                "database": _health_cache["result"],
            },
            "uptime_seconds": round(time.time() - start, 3),
            "timestamp": int(time.time()),
        }

        status_code = 200 if ok else 503
        if status_code != 200:
            logger.warning("Readiness check failed: %s", message)

        return JSONResponse(status_code=status_code, content=payload)
