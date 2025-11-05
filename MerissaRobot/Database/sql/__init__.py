# MerissaRobot/Database/sql/__init__.py
import asyncio
from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import DB_URL as DB_URI
from MerissaRobot import LOGGER as log

# Heroku style postgres url fix
if DB_URI and DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)

# Decide async vs sync by presence of "asyncpg" in the URI
if DB_URI and "asyncpg" in DB_URI:
    log.info("[PostgreSQL] Using asyncpg async engine.")
    # Create async engine
    ENGINE = create_async_engine(DB_URI, future=True)
    BASE = declarative_base()
    # Scoped session using AsyncSession class
    SESSION = scoped_session(sessionmaker(bind=ENGINE, class_=AsyncSession, expire_on_commit=False))

    # Create tables (async engines require run_sync)
    async def _create_all_async():
        log.info("[PostgreSQL] Creating tables (async)...")
        async with ENGINE.begin() as conn:
            await conn.run_sync(BASE.metadata.create_all)
        log.info("[PostgreSQL] Tables created (async).")

    try:
        asyncio.get_event_loop().run_until_complete(_create_all_async())
    except RuntimeError:
        # If event loop is already running (rare in some hosts), create a new one
        new_loop = asyncio.new_event_loop()
        try:
            new_loop.run_until_complete(_create_all_async())
        finally:
            new_loop.close()

    log.info("[PostgreSQL] Async connection successful, session started.")

else:
    log.info("[PostgreSQL] Using synchronous engine.")
    ENGINE = create_sync_engine(DB_URI, future=True)
    BASE = declarative_base()
    SESSION = scoped_session(sessionmaker(bind=ENGINE, autoflush=False))
    try:
        log.info("[PostgreSQL] Creating tables (sync)...")
        BASE.metadata.create_all(ENGINE)
        log.info("[PostgreSQL] Tables created (sync).")
    except Exception as e:
        log.exception(f"[PostgreSQL] Failed to create tables: {e}")
        raise

    log.info("[PostgreSQL] Connection successful, session started.")
