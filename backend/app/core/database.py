from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://yukti_user:yukti_password_secure@db:5432/yukti_db"

# ENTERPRISE TUNING: Sized for 1000+ concurrent users
engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    pool_size=50,        # Keep 50 base connections open
    max_overflow=100,    # Allow bursting up to 150 total concurrent DB connections
    pool_timeout=30,     # Wait 30s for a connection before throwing 500
    pool_pre_ping=True   # Verify connections are alive before using (prevents stale drops)
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
