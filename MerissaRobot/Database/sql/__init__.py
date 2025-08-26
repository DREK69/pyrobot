from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from config import DB_URL as DB_URI
from MerissaRobot import LOGGER as log

if DB_URI and DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)

engine = create_engine(DB_URI, client_encoding="utf8")
BASE = declarative_base()
SESSION = scoped_session(sessionmaker(bind=engine, autoflush=False))

try:
    log.info("[PostgreSQL] Connecting to database...")
    BASE.metadata.create_all(engine)   # <-- Yahi sabse important hai
    log.info("[PostgreSQL] Tables created (if not exist).")
except Exception as e:
    log.exception(f"[PostgreSQL] Failed to connect due to {e}")
    exit()

log.info("[PostgreSQL] Connection successful, session started.")
