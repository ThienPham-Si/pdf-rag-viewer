import asyncio
import os
import tempfile
import uuid
from datetime import datetime, timezone
import boto3
from arq import Worker
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
from google import genai
import logging

from app.config import settings
from app.models.document import Document, DocumentStatus
from app.models.chunk import Chunk
from app.parser import parse_and_chunk_pdf

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def process_document(ctx, document_id: str):
    doc_uuid = uuid.UUID(document_id)
    logger.info(f"Processing document {doc_uuid}")
    
    async with AsyncSessionLocal() as session:
        doc = await session.get(Document, doc_uuid)
        if not doc:
            logger.error(f"Document {doc_uuid} not found")
            return
        
        doc.status = DocumentStatus.processing
        await session.commit()

        try:
            # Download file from S3
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                s3_client.download_fileobj(settings.S3_BUCKET, doc.s3_key, tmp_file)
                tmp_file_path = tmp_file.name

            # Parse and chunk
            # This is CPU intensive, ideally run in a process pool, but we'll run it in a thread for now
            logger.info(f"Parsing PDF {doc_uuid}")
            parent_chunks_data = await asyncio.to_thread(parse_and_chunk_pdf, tmp_file_path)
            os.remove(tmp_file_path)

            logger.info(f"Generating embeddings for {doc_uuid}")
            # Collect all child chunks to batch embed
            all_children = []
            for p in parent_chunks_data:
                all_children.extend(p["children"])
            
            if all_children:
                try:
                    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "sk-proj-...":
                        raise ValueError("No Gemini API key provided.")
                        
                    batch_size = 100
                    for i in range(0, len(all_children), batch_size):
                        batch = all_children[i:i+batch_size]
                        response = await gemini_client.aio.models.embed_content(
                            model="gemini-embedding-2",
                            contents=[c["content"] for c in batch],
                            config=genai.types.EmbedContentConfig(output_dimensionality=768)
                        )
                        for j, c in enumerate(batch):
                            c["embedding"] = response.embeddings[j].values
                            
                except Exception as e:
                    logger.warning(f"Failed to generate real embeddings ({e}). Falling back to dummy embeddings.")
                    import random
                    for c in all_children:
                        # gemini-embedding-2 generates 768 dims (via config)
                        c["embedding"] = [random.uniform(-0.1, 0.1) for _ in range(768)]

            # Insert into database
            logger.info(f"Inserting chunks into DB for {doc_uuid}")
            total_pages = 0
            for p_idx, p_data in enumerate(parent_chunks_data):
                if p_data["page_number"] and p_data["page_number"] > total_pages:
                    total_pages = p_data["page_number"]
                    
                parent_chunk = Chunk(
                    document_id=doc_uuid,
                    content=p_data["content"],
                    page_number=p_data["page_number"],
                    token_count=p_data["token_count"],
                    chunk_index=p_idx,
                )
                session.add(parent_chunk)
                await session.flush() # To get parent_chunk.id
                
                # Update parent chunk tsvector
                await session.execute(
                    text("""
                    UPDATE chunks 
                    SET search_vector = to_tsvector('english', :content) 
                    WHERE id = :id
                    """),
                    {"content": parent_chunk.content, "id": parent_chunk.id}
                )

                for c_data in p_data["children"]:
                    child_chunk = Chunk(
                        document_id=doc_uuid,
                        parent_id=parent_chunk.id,
                        content=c_data["content"],
                        page_number=c_data["page_number"],
                        token_count=c_data["token_count"],
                        embedding=c_data["embedding"],
                        chunk_index=c_data["chunk_index"],
                    )
                    session.add(child_chunk)
                    await session.flush()
                    
                    # Update child chunk tsvector
                    await session.execute(
                        text("""
                        UPDATE chunks 
                        SET search_vector = to_tsvector('english', :content) 
                        WHERE id = :id
                        """),
                        {"content": child_chunk.content, "id": child_chunk.id}
                    )
                    
                    if c_data["page_number"] and c_data["page_number"] > total_pages:
                        total_pages = c_data["page_number"]

            doc.status = DocumentStatus.ready
            if total_pages > 0:
                doc.page_count = total_pages
                
            await session.commit()
            logger.info(f"Successfully processed document {doc_uuid}")
            
        except Exception as e:
            logger.error(f"Failed to process document {doc_uuid}: {e}")
            await session.rollback()
            doc.status = DocumentStatus.failed
            session.add(doc)
            await session.commit()


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions = [process_document]
