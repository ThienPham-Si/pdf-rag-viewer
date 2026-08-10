from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import uuid

from app.auth import get_current_user_id
from app.database import get_db_session
from app.models.tenant import Tenant

async def get_current_tenant(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
) -> Tenant:
    # Check if tenant exists
    stmt = select(Tenant).where(Tenant.clerk_user_id == user_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        # Create tenant
        tenant = Tenant(clerk_user_id=user_id)
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)

    # Set local variable for RLS
    # Since we are using an asyncpg driver, we can use the set_config function or SET LOCAL
    await db.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant.id}'"))
    
    return tenant
