"""
MerissaRobot __init__.py
"""

import asyncio
import os
import sys
import time
from logging import (
    INFO,
    ERROR,
    StreamHandler,
    basicConfig,
    getLogger,
    handlers,
)

import spamwatch
from aiohttp import ClientSession
from pyrogram import Client
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyromod import listen  # ignore
from pytgcalls import PyTgCalls
from telethon import TelegramClient
from telethon.sessions import MemorySession

from telegram.ext import Application
from config import *

# ───────────────────────────────
# Logging
# ───────────────────────────────
StartTime = time.time()
LOGGER = getLogger("[MerissaRobot]")

basicConfig(
    level=INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s.%(funcName)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        handlers.RotatingFileHandler("log.txt", mode="w+", maxBytes=1000000),
        StreamHandler(),
    ],
)

getLogger("pyrogram").setLevel(ERROR)
getLogger("telethon").setLevel(ERROR)
getLogger("telegram").setLevel(ERROR)

# ───────────────────────────────
# Event Loop Setup
# ───────────────────────────────
def setup_event_loop():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Loop closed")
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass

    return asyncio.get_event_loop()

EVENT_LOOP = setup_event_loop()

# ───────────────────────────────
# PTB v22 Application
# ───────────────────────────────
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
    try:
        me = await application.bot.get_me()
        BOT_ID = me.id
        BOT_USERNAME = me.username
        BOT_NAME = me.first_name
        LOGGER.info(f"Bot initialized: {BOT_NAME} (@{BOT_USERNAME})")
    except Exception as e:
        LOGGER.error(f"Failed to initialize bot: {e}")
        raise

# ───────────────────────────────
# Clients
# ───────────────────────────────
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

if STRING_SESSION and STRING_SESSION.strip():
    user = Client(
        "MerissaMusic",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=str(STRING_SESSION),
        in_memory=True,
    )
    pytgcalls = PyTgCalls(user)

telethn = TelegramClient(MemorySession(), API_ID, API_HASH)

# ───────────────────────────────
DEV_USERS.add(OWNER_ID)
sw = None

def dirr():
    for file in os.listdir():
        if file.endswith((".jpg", ".jpeg")):
            os.remove(file)
    if "downloads" not in os.listdir():
        os.mkdir("downloads")
    LOGGER.info("Directories Updated.")

DRAGONS = list(DRAGONS) + list(DEV_USERS)
DEV_USERS = list(DEV_USERS)

# ───────────────────────────────
# Client Management
# ───────────────────────────────
_clients_started = False

async def initiate_clients():
    global _clients_started
    if _clients_started:
        return
    try:
        LOGGER.info("Starting clients...")
        if not pbot.is_connected:
            await pbot.start()
            LOGGER.info("Pyrogram Bot started")
        if user and not user.is_connected:
            await user.start()
            LOGGER.info("Userbot started")
            if pytgcalls and not pytgcalls.is_connected:
                await pytgcalls.start()
                LOGGER.info("PyTgCalls started")
        if not telethn.is_connected():
            await telethn.start(bot_token=TOKEN)
            LOGGER.info("Telethon started")

        _clients_started = True
        LOGGER.info("All clients initialized")

        try:
            await pbot.send_message(-1002846516370, "✅ Bot Started")
            if user:
                await user.send_message(-1002846516370, "✅ Assistant Started")
        except Exception as e:
            LOGGER.warning(f"Failed to send startup messages: {e}")

    except FloodWait as e:
        LOGGER.info(f"FloodWait {e.value}s")
        await asyncio.sleep(e.value)
        _clients_started = False
        await initiate_clients()
    except Exception as e:
        LOGGER.error(f"Error starting clients: {e}")
        raise

async def stop_clients():
    global _clients_started
    try:
        if pytgcalls:
            await pytgcalls.stop()
            LOGGER.info("PyTgCalls stopped")
        if user and user.is_connected:
            await user.stop()
            await user.storage.close()
            LOGGER.info("Userbot stopped")
        if pbot.is_connected:
            await pbot.stop()
            await pbot.storage.close()
            LOGGER.info("Pyrogram Bot stopped")
        if telethn.is_connected():
            await telethn.disconnect()
            LOGGER.info("Telethon disconnected")

        _clients_started = False
    except Exception as e:
        LOGGER.error(f"Error stopping clients: {e}")

async def graceful_shutdown():
    try:
        await stop_clients()
        if hasattr(application, "running") and application.running:
            await application.stop()
            LOGGER.info("PTB stopped")
        if hasattr(application, "shutdown"):
            await application.shutdown()
            LOGGER.info("PTB shutdown")
        await asyncio.sleep(0.5)
    finally:
        pending = [t for t in asyncio.all_tasks() if not t.done()]
        if pending:
            LOGGER.info(f"Cancelling {len(pending)} tasks...")
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)

# ───────────────────────────────
# Module Loader
# ───────────────────────────────
def load_all_modules():
    try:
        from MerissaRobot.Modules import ALL_MODULES
        LOGGER.info(f"Modules loaded: {ALL_MODULES}")
        return ALL_MODULES
    except Exception as e:
        LOGGER.error(f"Failed to load modules: {e}")
        return []
