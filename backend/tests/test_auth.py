import pytest
from httpx import AsyncClient
from unittest.mock import patch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from app.models.tenant import Tenant
from app.config import settings

@pytest.mark.asyncio
async def test_auth_missing_token(client: AsyncClient):
    # 401 without token
    response = await client.get("/documents")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

@pytest.mark.asyncio
async def test_auth_valid_token_auto_creates_tenant(client: AsyncClient):
    clerk_user_id = "user_test_123"

    with patch("app.auth.verify_token") as mock_verify:
        mock_verify.return_value = {"sub": clerk_user_id}
        
        # 200 with valid token
        response = await client.get("/documents", headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200
        assert response.json() == []

        # Check that Tenant was auto-created
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            result = await conn.execute(
                select(Tenant).where(Tenant.clerk_user_id == clerk_user_id)
            )
            tenant = result.mappings().one_or_none()
            assert tenant is not None
            assert tenant["clerk_user_id"] == clerk_user_id
        await engine.dispose()
