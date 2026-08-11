import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from app.worker import process_document
from app.models.document import Document, DocumentStatus
from app.models.chunk import Chunk
from app.config import settings

@pytest.mark.asyncio
async def test_worker_processing(client: AsyncClient):
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    with patch("app.auth.verify_token") as mock_verify, \
         patch("app.main.upload_file_to_s3") as mock_s3, \
         patch("app.worker.s3_client") as mock_worker_s3, \
         patch("app.worker.openai_client") as mock_openai, \
         patch("app.worker.parse_and_chunk_pdf") as mock_parse:
             
        mock_verify.return_value = {"sub": "user_test_worker"}
        mock_s3.return_value = True
        
        # Mock download_fileobj to just create an empty file
        def mock_download(bucket, key, fileobj):
            fileobj.write(b"dummy")
        mock_worker_s3.download_fileobj.side_effect = mock_download
        
        # Mock parsing to return fake chunks
        mock_parse.return_value = [
            {
                "content": "Parent chunk content",
                "token_count": 100,
                "page_number": 1,
                "children": [
                    {
                        "content": "Child chunk content",
                        "token_count": 50,
                        "page_number": 1,
                        "chunk_index": 0
                    }
                ]
            }
        ]
        
        # Mock OpenAI embeddings
        class FakeResponse:
            class FakeData:
                embedding = [0.1] * 1536
            data = [FakeData()]
            
        mock_openai.embeddings.create = AsyncMock(return_value=FakeResponse())

        # 1. Upload Document
        files = {"file": ("test_worker.pdf", b"dummy pdf content", "application/pdf")}
        response = await client.post(
            "/documents/upload",
            headers={"Authorization": "Bearer test_token"},
            files=files
        )
        assert response.status_code == 200
        data = response.json()
        doc_id = data["id"]
        
        # 2. Run Worker Manually (to simulate processing without starting ARQ in test)
        await process_document(None, doc_id)
        
        # 3. Verify Document is ready
        async with AsyncSessionLocal() as session:
            doc = await session.get(Document, uuid.UUID(doc_id))
            assert doc is not None
            assert doc.status == DocumentStatus.ready
            
            # Verify Chunks
            stmt = select(Chunk).where(Chunk.document_id == uuid.UUID(doc_id))
            result = await session.execute(stmt)
            chunks = result.scalars().all()
            
            assert len(chunks) == 2 # 1 parent, 1 child
            
            parent_chunk = next(c for c in chunks if c.parent_id is None)
            child_chunk = next(c for c in chunks if c.parent_id is not None)
            
            assert parent_chunk.content == "Parent chunk content"
            assert child_chunk.content == "Child chunk content"
            assert child_chunk.embedding is not None
            assert len(child_chunk.embedding) == 1536
            
            # search_vector is populated by db
            # We can test if it's not null by checking directly via raw SQL or wait for DB flush
            # But the ORM may not have fetched it if it wasn't requested or populated.
            # Let's query it explicitly
            stmt_sv = select(Chunk.search_vector).where(Chunk.id == child_chunk.id)
            sv_result = await session.execute(stmt_sv)
            sv = sv_result.scalar_one_or_none()
            assert sv is not None
