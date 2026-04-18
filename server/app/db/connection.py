from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

from server.app.config import settings
from server.app.db.models import Base

raw_db_url = settings.TURSO_DATABASE_URL
host = raw_db_url.replace("libsql://", "")

engine = create_async_engine(
    f"sqlite+aiolibsql://{host}?secure=true",
    poolclass=AsyncAdaptedQueuePool,
    connect_args={"auth_token": settings.TURSO_AUTH_TOKEN},
    echo=False,
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
