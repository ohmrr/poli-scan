import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

from server.app.db.models import Base

load_dotenv()

raw_db_url = os.getenv("TURSO_DATABASE_URL")
host = raw_db_url.replace("libsql://", "")

engine = create_async_engine(
    f"sqlite+aiolibsql://{host}?secure=true",
    poolclass=AsyncAdaptedQueuePool,
    connect_args={"auth_token": os.getenv("TURSO_AUTH_TOKEN")},
    echo=True,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
