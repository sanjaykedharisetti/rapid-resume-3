"""
SQLAlchemy async database setup.
Supports SQLite (development) and PostgreSQL (production) through DATABASE_URL env var.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# Create async engine – connect_args only needed for SQLite
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Create all tables on startup and apply non-destructive schema migrations."""
    from sqlalchemy import text
    async with engine.begin() as conn:
        from app.models import analysis  # noqa: F401 – ensure models are registered
        await conn.run_sync(Base.metadata.create_all)

        # Non-destructive migrations for existing SQLite databases
        for col, col_type in [
            ("resume_text", "TEXT"),
            ("job_description", "TEXT"),
            ("optimized_score", "FLOAT"),
            ("optimization_summary", "TEXT"),
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE analysis_records ADD COLUMN {col} {col_type}"))
            except Exception:
                pass  # column already exists or table freshly created


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
