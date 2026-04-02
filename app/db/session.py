from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import Settings

engine = create_async_engine(
    Settings().DATABASE_URL,
    echo=True,
    pool_timeout=30,  
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)
