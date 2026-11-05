import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, make_asgi_app
from redis import Redis
from sqlalchemy import text

from app.api.v1 import (
    auth, audit, dashboard, leaks, notifications, reports, resets, roles, sources, users, webhooks,
)
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.scheduler import start_scheduler, stop_scheduler
from app.db.session import engine

configure_logging()
logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter("radar_requests_total", "Total requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("radar_request_latency_seconds", "Latency", ["method", "path"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando %s v%s (%s)", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)
    start_scheduler()
    yield
    stop_scheduler()
    logger.info("Aplicación detenida")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "prod" else None,
    redoc_url="/redoc" if settings.APP_ENV != "prod" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        REQUEST_COUNT.labels(request.method, request.url.path, "500").inc()
        raise
    elapsed = time.perf_counter() - start
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(elapsed)
    response.headers["X-Process-Time"] = f"{elapsed:.4f}"
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Error interno"})


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/ready", tags=["health"])
def ready():
    dependencies = {"postgres": "unavailable", "redis": "skipped"}
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        dependencies["postgres"] = "ok"
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail={"status": "not_ready", "dependencies": dependencies})
    if settings.REDIS_REQUIRED:
        try:
            client = Redis.from_url(str(settings.REDIS_URL), socket_connect_timeout=1,
                                    socket_timeout=1)
            client.ping()
            client.close()
            dependencies["redis"] = "ok"
        except Exception:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail={"status": "not_ready", "dependencies": dependencies})
    return {"status": "ready", "dependencies": dependencies}


if settings.METRICS_ENABLED:
    app.mount("/metrics", make_asgi_app())

API = settings.API_V1_PREFIX
app.include_router(auth.router, prefix=API)
app.include_router(notifications.router, prefix=API)
app.include_router(roles.router, prefix=API)
app.include_router(users.router, prefix=API)
app.include_router(leaks.router, prefix=API)
app.include_router(resets.router, prefix=API)
app.include_router(dashboard.router, prefix=API)
app.include_router(reports.router, prefix=API)
app.include_router(audit.router, prefix=API)
app.include_router(sources.router, prefix=API)
app.include_router(webhooks.router, prefix=API)
