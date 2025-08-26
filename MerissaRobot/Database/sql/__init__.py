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

# IMPORTANT: Import all your models here BEFORE create_all()
from MerissaRobot.Database.sql.connection_sql import (
    ChatAccessConnectionSettings, 
    Connection, 
    ConnectionHistory
)

# Import any other models you have
# from MerissaRobot.Database.sql.other_model import OtherModel

try:
    log.info("[PostgreSQL] Connecting to database...")
    BASE.metadata.create_all(ENGINE)
    log.info("[PostgreSQL] Tables created (if not exist).")
except Exception as e:
    log.exception(f"[PostgreSQL] Failed to connect due to {e}")
    exit()

log.info("[PostgreSQL] Connection successful, session started.")

# Alternative approach - if you want to import in your main bot file
# MerissaRobot/__main__.py or wherever you start your bot

# Import models before starting the bot
import MerissaRobot.Database.sql.connection_sql  # This will register the models

# Start your bot after this
