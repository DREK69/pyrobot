"""
MerissaRobot __init__.py — unified startup for PTB + Pyrogram + Telethon + PyTgCalls
"""

import asyncio
import os
import sys
import time
import re
from typing import List, Optional, Union

import spamwatch  # noqa: F401
from aiohttp import ClientSession  # noqa: F401
from pyrogram import Client
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyromod import listen  # noqa: F401  (pyromod monkeypatch)
from pytgcalls import PyTgCalls
from telethon import TelegramClient
from telethon.sessions import MemorySession

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters as F,
)

from logging import INFO, ERROR, StreamHandler, basicConfig, getLogger
from logging.handlers import RotatingFileHandler

# ----------------------- Project Config -----------------------
from config import *  # noqa: F401,F403

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
    global BOT_ID, BOT_USERNAME, BOT_NAME
    me = await application.bot.get_me()
    BOT_ID = me.id
    BOT_USERNAME = me.username
    BOT_NAME = me.first_name
    LOGGER.info(f"Bot initialized: {BOT_NAME} (@{BOT_USERNAME})")

ASS_ID = "7946751397"
ASS_NAME = "Merissa Assistant"
ASS_USERNAME = "Cjjdjdjjdj"
ASS_MENTION = "https://t.me/Cjjdjdjjdj"

# ----------------------- Pyrogram / Telethon ------------------
pbot = None
user = None
pytgcalls = None
telethn = None

# --------------------- SpamWatch / Misc -----------------------
DEV_USERS.add(OWNER_ID)
sw = None

def dirr():
    for file in os.listdir():
        if file.lower().endswith((".jpg", ".jpeg")):
            try:
                os.remove(file)
            except Exception:
                pass
    if "downloads" not in os.listdir():
        os.mkdir("downloads")
    LOGGER.info("Directories Updated.")

def _as_set(x):
    if x is None:
        return set()
    if isinstance(x, set):
        return x
    if isinstance(x, (list, tuple)):
        return set(x)
    return {x}

_DEV_USERS_SET = _as_set(DEV_USERS)
_DRAGONS_SET   = _as_set(DRAGONS) | _DEV_USERS_SET
_WOLVES_SET    = _as_set(WOLVES)
_DEMONS_SET    = _as_set(DEMONS)
_TIGERS_SET    = _as_set(TIGERS)

IMMUNE_USERS_SET = _DRAGONS_SET | _WOLVES_SET | _DEMONS_SET | _TIGERS_SET | _DEV_USERS_SET

DEV_USERS  = list(_DEV_USERS_SET)
DRAGONS    = list(_DRAGONS_SET)
WOLVES     = list(_WOLVES_SET)
DEMONS     = list(_DEMONS_SET)
TIGERS     = list(_TIGERS_SET)
IMMUNE_USERS = list(IMMUNE_USERS_SET)

# ---------------------- Custom Handlers (PTB) -----------------
class CustomCommandHandler(CommandHandler):
    def __init__(self, command: Union[str, List[str]], callback, flt=None,
                 block: bool = True, has_args: Optional[int] = None, **kwargs):
        if flt is None:
            flt = ~F.UpdateType.EDITED_MESSAGE
        super().__init__(command=command, callback=callback, filters=flt, block=block, **kwargs)
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
    def __init__(self, flt, callback, block: bool = True, **kwargs):
        if flt is None:
            flt = F.ALL
        super().__init__(filters=flt, callback=callback, block=block, **kwargs)

class CustomRegexHandler(MessageHandler):
    def __init__(self, pattern: Union[str, re.Pattern], callback, block: bool = True, **kwargs):
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        super().__init__(filters=F.Regex(pattern), callback=callback, block=block, **kwargs)

# ----------------------- Client Management --------------------
_clients_started = False

async def initiate_clients():
    """Initialize all clients dynamically (after loop exists)."""
    global _clients_started, pbot, user, pytgcalls, telethn
    if _clients_started:
        return
    try:
        LOGGER.info("Starting clients initialization...")

        if pbot is None:
            pbot = Client(
                "MerissaRobot",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=TOKEN,
                workers=10,
                in_memory=True,
            )
        if not pbot.is_connected:
            await pbot.start()
            LOGGER.info("Pyrogram Bot started")

        if STRING_SESSION and user is None:
            user = Client(
                "MerissaMusic",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=str(STRING_SESSION),
                in_memory=True,
            )
        if user and not user.is_connected:
            await user.start()
            LOGGER.info("Pyrogram User started")

            if pytgcalls is None:
                pytgcalls = PyTgCalls(user)
            if not pytgcalls.is_connected:
                await pytgcalls.start()
                LOGGER.info("PyTgCalls started")

        if telethn is None:
            telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
        if not telethn.is_connected():
            await telethn.start(bot_token=TOKEN)
            LOGGER.info("Telethon started")

        _clients_started = True
        LOGGER.info("All clients initialized successfully")

    except FloodWait as e:
        LOGGER.info(f"FloodWait: Need to wait {e.value} seconds")
        await asyncio.sleep(e.value)
        _clients_started = False
        await initiate_clients()
    except Exception as e:
        LOGGER.error(f"Error starting clients: {e}")
        raise

# ------------------------- Exports ----------------------------
userbot = user

__all__ = [
    "application", "init_bot", "setup_handlers",
    "pbot", "user", "userbot", "telethn", "pytgcalls",
    "DEV_USERS", "DRAGONS", "WOLVES", "DEMONS", "TIGERS",
    "IMMUNE_USERS", "IMMUNE_USERS_SET",
    "dirr", "initiate_clients", "stop_clients", "graceful_shutdown",
    "ALL_MODULES", "load_all_modules",
]
