from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.core.config import settings
from app.core.logging import logger

Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

async def init_db():
    """Initialize PostgreSQL extensions and database schema."""
    try:
        async with engine.begin() as conn:
            # Enable pgvector extension
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            # Enable uuid-ossp extension
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
            # Create GIN index on transcript chunks for full-text search
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_transcript_chunks_tsv 
                ON transcript_chunks USING GIN(tsv);
            """))
            # Create HNSW/IVFFlat index for vector cosine similarity if table exists
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_transcript_chunks_vector 
                ON transcript_chunks USING hnsw (embedding vector_cosine_ops);
            """))
        logger.info("Database initialized successfully with pgvector and full-text search indexes.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e
