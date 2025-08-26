# MerissaRobot/Database/sql/__init__.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from config import DB_URL as DB_URI
from MerissaRobot import LOGGER as log

if DB_URI and DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)

ENGINE = create_engine(DB_URI, client_encoding="utf8")
BASE = declarative_base()
SESSION = scoped_session(sessionmaker(bind=ENGINE, autoflush=False))

try:
    log.info("[PostgreSQL] Connecting to database...")
    
    # Import all models BEFORE create_all() but don't run any queries yet
    from MerissaRobot.Database.sql.connection_sql import (
        ChatAccessConnectionSettings, 
        Connection, 
        ConnectionHistory
    )
    
    # Create all tables
    BASE.metadata.create_all(ENGINE)
    log.info("[PostgreSQL] Tables created (if not exist).")
    
    # Now initialize connection history after tables are created
    from MerissaRobot.Database.sql.connection_sql import init_connection_history
    init_connection_history()
    
except Exception as e:
    log.exception(f"[PostgreSQL] Failed to connect due to {e}")
    exit()

log.info("[PostgreSQL] Connection successful, session started.")
