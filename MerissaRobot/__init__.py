"""
MerissaRobot __init__.py — unified startup for PTB + Pyrogram + Telethon + PyTgCalls
"""

import asyncio
import os
import sys
import time
import re
from typing import List, Optional, Union

import spamwatch
from aiohttp import ClientSession
from pyrogram import Client
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyromod import listen  # noqa: F401  (pyromod monkeypatch)
from pytgcalls import PyTgCalls
from telethon import TelegramClient
from telethon.sessions import MemorySession

from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import Update

from logging import INFO, ERROR, StreamHandler, basicConfig, getLogger
from logging.handlers import RotatingFileHandler

# ----------------------- Project Config -----------------------
from config import *  # noqa: F401,F403  (expects TOKEN, API_ID, API_HASH, STRING_SESSION, role lists/sets, etc.)

# ----------------------- Logging Setup ------------------------
StartTime = time.time()
LOGGER = getLogger("[MerissaRobot]")

basicConfig(
    level=INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s.%(funcName)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", mode="w+", maxBytes=1_000_000, backupCount=1),
        StreamHandler(),
    ],
)

getLogger("pyrogram").setLevel(ERROR)
getLogger("telethon").setLevel(ERROR)
getLogger("telegram").setLevel(ERROR)

# ---------------- Event Loop: single policy for all -----------
def setup_event_loop():
    """Create/return a single event loop with best policy."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Loop is closed")
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if sys.platform.startswith("win"):
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass
    else:
        try:
            import uvloop  # type: ignore
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except Exception:
            pass

    return loop

EVENT_LOOP = setup_event_loop()

# --------------------- PTB v22 Application --------------------
application = (
    Application.builder()
    .token(TOKEN)
    .concurrent_updates(True)
    .build()
)

BOT = application.bot
BOT_ID = None
BOT_USERNAME = None
BOT_NAME = None
BOT_MENTION = "https://t.me/MerissaRobot"

async def init_bot():
    """Fetch bot identity (PTB) once application is initialized."""
    global BOT_ID, BOT_USERNAME, BOT_NAME
    try:
        me = await application.bot.get_me()
        BOT_ID = me.id
        BOT_USERNAME = me.username
        BOT_NAME = me.first_name
        LOGGER.info(f"Bot initialized: {BOT_NAME} (@{BOT_USERNAME})")
    except Exception as e:
        LOGGER.error(f"Failed to initialize bot: {e}")
        raise

# ----------------------- Pyrogram / Telethon ------------------
pbot = Client(
    "MerissaRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    workers=10,
    in_memory=True,
)

user = None
pytgcalls = None

if STRING_SESSION and str(STRING_SESSION).strip():
    user = Client(
        "MerissaMusic",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=str(STRING_SESSION),
        in_memory=True,
    )
    pytgcalls = PyTgCalls(user)

telethn = TelegramClient(MemorySession(), API_ID, API_HASH)

# --------------------- SpamWatch / Misc -----------------------
DEV_USERS.add(OWNER_ID)  # ensure owner is always dev
sw = None  # you can initialize later if you have token/endpoint

def dirr():
    """Clean loose files & ensure folders exist."""
    for file in os.listdir():
        if file.lower().endswith((".jpg", ".jpeg")):
            try:
                os.remove(file)
            except Exception:
                pass
    if "downloads" not in os.listdir():
        os.mkdir("downloads")
    LOGGER.info("Directories Updated.")

# --------------- Roles: normalize types (avoid list+set) ------
def _as_set(x):
    if x is None:
        return set()
    if isinstance(x, set):
        return x
    if isinstance(x, (list, tuple)):
        return set(x)
    return {x}

# Convert everything to sets first
_DEV_USERS_SET = _as_set(DEV_USERS)
_DRAGONS_SET   = _as_set(DRAGONS) | _DEV_USERS_SET  # dragons always include devs
_WOLVES_SET    = _as_set(WOLVES)
_DEMONS_SET    = _as_set(DEMONS)
_TIGERS_SET    = _as_set(TIGERS)

# Unified set for membership checks
IMMUNE_USERS_SET = _DRAGONS_SET | _WOLVES_SET | _DEMONS_SET | _TIGERS_SET | _DEV_USERS_SET

# Also export list versions (for legacy code that concatenates lists)
DEV_USERS  = list(_DEV_USERS_SET)
DRAGONS    = list(_DRAGONS_SET)
WOLVES     = list(_WOLVES_SET)
DEMONS     = list(_DEMONS_SET)
TIGERS     = list(_TIGERS_SET)
IMMUNE_USERS = list(IMMUNE_USERS_SET)

# ---------------------- Custom Handlers (PTB) -----------------
class CustomCommandHandler(CommandHandler):
    """Custom Command Handler compatible with PTB v22 (optional arg-count gate)."""
    def __init__(
        self,
        command: Union[str, List[str]],
        callback,
        filters=None,
        block: bool = True,
        has_args: Optional[int] = None,
        **kwargs
    ):
        if filters is None:
            filters = ~filters.UpdateType.EDITED_MESSAGE
        super().__init__(command=command, callback=callback, filters=filters, block=block, **kwargs)
        self.has_args = has_args

    def check_update(self, update: object) -> Optional[bool]:
        if not super().check_update(update):
            return None
        if self.has_args is not None:
            message = getattr(update, "effective_message", None)
            if message and message.text:
                args = message.text.split()[1:]
                if len(args) < self.has_args:
                    return None
        return True

class CustomMessageHandler(MessageHandler):
    def __init__(self, filters, callback, block: bool = True, **kwargs):
        if filters is None:
            filters = filters.ALL
        super().__init__(filters=filters, callback=callback, block=block, **kwargs)

class CustomRegexHandler(MessageHandler):
    def __init__(self, pattern: Union[str, re.Pattern], callback, block: bool = True, **kwargs):
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        super().__init__(filters=filters.Regex(pattern), callback=callback, block=block, **kwargs)

# ----------------------- Client Management --------------------
_clients_started = False

async def initiate_clients():
    """Initialize all clients in controlled manner."""
    global _clients_started
    if _clients_started:
        return
    try:
        LOGGER.info("Starting clients initialization...")

        # Pyrogram Bot
        if not pbot.is_connected:
            await pbot.start()
            LOGGER.info("Pyrogram Bot started")

        # Pyrogram User + PyTgCalls
        if user and not user.is_connected:
            await user.start()
            LOGGER.info("Pyrogram User started")

            if pytgcalls and not pytgcalls.is_connected:
                await pytgcalls.start()
                LOGGER.info("PyTgCalls started")

        # Telethon (bot session)
        if not telethn.is_connected():
            await telethn.start(bot_token=TOKEN)
            LOGGER.info("Telethon started")

        _clients_started = True
        LOGGER.info("All clients initialized successfully")

        # Optional: startup pings (safe)
        try:
            STARTUP_CHAT = int(os.environ.get("STARTUP_CHAT", "-1002846516370"))
            await pbot.send_message(STARTUP_CHAT, "✅ Bot Started")
            if user:
                await user.send_message(STARTUP_CHAT, "✅ Assistant Started")
        except Exception as e:
            LOGGER.warning(f"Failed to send startup messages: {e}")

    except FloodWait as e:
        LOGGER.info(f"FloodWait: Need to wait {e.value} seconds")
        await asyncio.sleep(e.value)
        _clients_started = False
        await initiate_clients()
    except Exception as e:
        LOGGER.error(f"Error starting clients: {e}")
        raise

async def stop_clients():
    """Stop all clients in reverse order and cleanup tasks."""
    global _clients_started
    try:
        # Stop PyTgCalls first
        if pytgcalls and hasattr(pytgcalls, "stop"):
            try:
                await pytgcalls.stop()
                LOGGER.info("PyTgCalls stopped")
            except Exception as e:
                LOGGER.warning(f"Error stopping PyTgCalls: {e}")

        # Stop user (pyrogram)
        if user and user.is_connected:
            try:
                await user.stop()
                # close in-memory storage if present
                try:
                    await user.storage.close()
                except Exception:
                    pass
                LOGGER.info("Pyrogram User stopped")
            except Exception as e:
                LOGGER.warning(f"Error stopping User client: {e}")

        # Stop bot (pyrogram)
        if pbot.is_connected:
            try:
                await pbot.stop()
                try:
                    await pbot.storage.close()
                except Exception:
                    pass
                LOGGER.info("Pyrogram Bot stopped")
            except Exception as e:
                LOGGER.warning(f"Error stopping Bot client: {e}")

        # Telethon
        if telethn.is_connected():
            try:
                await telethn.disconnect()
                LOGGER.info("Telethon disconnected")
            except Exception as e:
                LOGGER.warning(f"Error disconnecting Telethon: {e}")

        _clients_started = False

        # Cancel leftover asyncio tasks related to third-party libs
        current_task = asyncio.current_task()
        all_tasks = [t for t in asyncio.all_tasks() if t is not current_task and not t.done()]
        if all_tasks:
            LOGGER.info(f"Cancelling {len(all_tasks)} pending tasks...")
            for task in all_tasks:
                task.cancel()
            try:
                await asyncio.gather(*all_tasks, return_exceptions=True)
                LOGGER.info("All pending tasks cancelled")
            except Exception as e:
                LOGGER.warning(f"Error cancelling tasks: {e}")

    except Exception as e:
        LOGGER.error(f"Error stopping clients: {e}")

async def graceful_shutdown():
    """Gracefully shutdown all components."""
    try:
        await stop_clients()
        if hasattr(application, "running") and application.running:
            try:
                await application.stop()
                LOGGER.info("PTB Application stopped")
            except Exception as e:
                LOGGER.warning(f"Error stopping PTB: {e}")
        if hasattr(application, "shutdown"):
            try:
                await application.shutdown()
                LOGGER.info("PTB Application shutdown")
            except Exception as e:
                LOGGER.warning(f"Error during PTB shutdown: {e}")

        # Tiny delay for cleanup
        await asyncio.sleep(0.3)

    except Exception as e:
        LOGGER.error(f"Error during graceful shutdown: {e}")
    finally:
        # Final task cleanup (if anything left)
        pending = [t for t in asyncio.all_tasks() if not t.done()]
        if pending:
            LOGGER.info(f"Final cleanup: cancelling {len(pending)} tasks...")
            for task in pending:
                task.cancel()
            try:
                await asyncio.gather(*pending, return_exceptions=True)
            except Exception:
                pass

# ------------------------- Module Loading ---------------------
def load_all_modules():
    """
    Import the modules registry from MerissaRobot.Modules.
    Make sure MerissaRobot/Modules/__init__.py defines ALL_MODULES.
    Example:

        # MerissaRobot/Modules/__init__.py
        from importlib import import_module
        ALL_MODULES = [
            "start",
            "help",
            "music",
            "ping",
            # ...
        ]
        for mod in ALL_MODULES:
            import_module(f"MerissaRobot.Modules.{mod}")
    """
    try:
        from MerissaRobot.Modules import ALL_MODULES  # noqa: F401
        LOGGER.info("Successfully loaded Modules: %s", str(ALL_MODULES))
        return ALL_MODULES
    except Exception as e:
        LOGGER.error(f"Failed to load modules: {e}")
        return []

# ------------------------- Exports ----------------------------
# Backward-compatible alias (some code imports userbot)
userbot = user

# Export commonly used symbols
__all__ = [
    # app/bot
    "application", "init_bot",
    # clients
    "pbot", "user", "userbot", "telethn", "pytgcalls",
    # roles (list + set)
    "DEV_USERS", "DRAGONS", "WOLVES", "DEMONS", "TIGERS",
    "IMMUNE_USERS", "IMMUNE_USERS_SET",
    # utils
    "dirr", "initiate_clients", "stop_clients", "graceful_shutdown",
    # modules
    "ALL_MODULES", "load_all_modules",
]

# Make ALL_MODULES available for `from MerissaRobot import ALL_MODULES`
ALL_MODULES = load_all_modules()
