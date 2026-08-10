from collections.abc import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    engine = request.app.state.db_engine
    # create session factory on the fly or just create a session
    session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
