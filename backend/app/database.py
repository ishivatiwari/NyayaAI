"""
Database setup with SQLAlchemy async.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from app.config import settings
import structlog

logger = structlog.get_logger()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def cleanup_failed_documents():
    """Clear stale failed document records from earlier broken runs so the app starts clean."""
    try:
        from app.models.document import Document
    except Exception:
        logger.warning("Document model not yet loaded; skipping cleanup of stale failed documents")
        return

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Document).where(Document.status == "failed"))
            failed_documents = result.scalars().all()
        except Exception:
            logger.warning("No document table available yet; skipping stale document cleanup")
            return

        for doc in failed_documents:
            try:
                if doc.file_path and os.path.exists(doc.file_path):
                    os.remove(doc.file_path)
            except Exception:
                pass
            await session.delete(doc)
        await session.commit()

    logger.info("Cleaned stale failed documents from previous runs")


async def init_db():
    """Create all tables and clear stale failed records on startup."""
    from app.models import document, analysis, conversation  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await cleanup_failed_documents()
    logger.info("Database initialized")


async def get_db():
    """Dependency: yield async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
