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
from app.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tenant import Tenant
from app.models.document import Document
from fastapi import Depends, UploadFile, File, HTTPException, status
from sqlalchemy import select
from app.s3 import upload_file_to_s3
import uuid

@app.get("/documents")
async def list_documents(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db_session)
):
    """List documents for the current tenant."""
    stmt = select(Document).where(
        Document.tenant_id == tenant.id,
        Document.deleted_at.is_(None)
    ).order_by(Document.created_at.desc())
    result = await db.execute(stmt)
    documents = result.scalars().all()
    
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.status,
            "page_count": doc.page_count,
            "created_at": doc.created_at
        }
        for doc in documents
    ]

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db_session)
):
    """Upload a new document."""
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # 50MB limit validation (using spooling if over a certain size, we can check file size)
    # UploadFile object in FastAPI has `size` property in python 3.10+ / starlette >= 0.28
    if getattr(file, "size", 0) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 50MB limit"
        )
        
    # Read first to verify actual size if file.size is not reliable
    # But usually file.size is populated. Alternatively we can read chunks.
    # Let's rely on file.size which is supported in recent FastAPI versions.
    
    document_id = uuid.uuid4()
    s3_key = f"{tenant.id}/{document_id}/{file.filename}"
    
    # Upload to MinIO
    # We can pass file.file to upload_fileobj
    upload_success = upload_file_to_s3(file.file, s3_key)
    if not upload_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage"
        )
    
    # Create DB record
    new_doc = Document(
        id=document_id,
        tenant_id=tenant.id,
        filename=file.filename,
        s3_key=s3_key,
        # status defaults to uploaded
    )
    db.add(new_doc)
    await db.commit()
    
    # TODO: Enqueue ARQ job here (04 - parsing pipeline)
    
    return {
        "id": new_doc.id,
        "filename": new_doc.filename,
        "status": new_doc.status,
        "created_at": new_doc.created_at
    }
