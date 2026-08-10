import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown resources."""
    app.state.db_engine = create_async_engine(settings.DATABASE_URL)
    app.state.redis = aioredis.from_url(settings.REDIS_URL)

    # Validate connections eagerly on startup
    try:
        async with app.state.db_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL connection verified")
    except Exception:
        logger.warning("PostgreSQL is not reachable at startup")

    try:
        await app.state.redis.ping()
        logger.info("Redis connection verified")
    except Exception:
        logger.warning("Redis is not reachable at startup")

    yield
    await app.state.db_engine.dispose()
    await app.state.redis.aclose()


app = FastAPI(title="Document Intelligence API", lifespan=lifespan)

# TODO: Lock down to the actual frontend origin in production.
# See ADR-0002: CORS must allow the Vercel frontend origin specifically.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Return connection status for Postgres and Redis.

    Always returns 200 — this is a health check, not a liveness probe.
    Individual services report 'connected' or 'disconnected'.
    """
    pg_status = await _check_postgres()
    redis_status = await _check_redis()

    all_connected = pg_status == "connected" and redis_status == "connected"

    return {
        "status": "healthy" if all_connected else "degraded",
        "postgres": pg_status,
        "redis": redis_status,
    }


async def _check_postgres() -> str:
    """Attempt a SELECT 1 on Postgres and return connection status."""
    try:
        async with app.state.db_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "connected"
    except Exception:
        return "disconnected"


async def _check_redis() -> str:
    """Attempt a PING on Redis and return connection status."""
    try:
        await app.state.redis.ping()
        return "connected"
    except Exception:
        return "disconnected"


from app.dependencies import get_current_tenant
from app.models.tenant import Tenant
from fastapi import Depends

@app.get("/documents")
async def list_documents(tenant: Tenant = Depends(get_current_tenant)):
    """List documents for the current tenant (placeholder)."""
    return []
