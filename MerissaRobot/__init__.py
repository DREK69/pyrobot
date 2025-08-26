import asyncio
import sys
import time
from logging import INFO, ERROR, StreamHandler, basicConfig, getLogger, handlers

from pyrogram import Client
from pytgcalls import PyTgCalls
from telethon import TelegramClient
from telethon.sessions import MemorySession
from telegram.ext import Application
from telegram import Update

from config import *

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

# PTB v22 Application
application = Application.builder().token(TOKEN).concurrent_updates(True).build()

# Pyrogram + Telethon
pbot = Client("MerissaRobot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN, workers=100)
user = Client("MerissaMusic", api_id=API_ID, api_hash=API_HASH, session_string=str(STRING_SESSION))
pytgcalls = PyTgCalls(user)
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)


async def start_all():
    """Start all clients and run PTB polling"""
    try:
        # start pyrogram + telethon + tgcalls
        await pbot.start()
        await user.start()
        await pytgcalls.start()
        await telethn.start(bot_token=TOKEN)

        LOGGER.info("Pyrogram, Telethon, PyTgCalls started")

        # start PTB polling (blocks until stopped)
        await application.run_polling(
            stop_signals=None,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )

    except Exception as e:
        LOGGER.error(f"Fatal error in start_all: {e}")
        raise
    finally:
        # cleanup
        await pbot.stop()
        await user.stop()
        await pytgcalls.stop()
        await telethn.disconnect()
        await application.shutdown()
        LOGGER.info("Bot stopped successfully")


if __name__ == "__main__":
    try:
        asyncio.run(start_all())
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"Fatal error: {e}")
        sys.exit(1)
